"""
通知服务 - 支持多种通知渠道和个性化模板
"""

import json
import logging
import requests
import hashlib
import hmac
import base64
import time
from typing import Dict, Any, List, Optional
from datetime import datetime


class NotifyService:
    """通知服务，支持多种通知渠道和个性化模板"""
    
    def __init__(self, config_manager):
        """
        初始化通知服务
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        
        # 初始化通知渠道
        self._init_channels()
    
    def _init_channels(self):
        """初始化通知渠道"""
        self.channels = {}
        
        # 钉钉通知
        dingtalk_config = self.config_manager.get_notification_config().get('dingtalk', {})
        if dingtalk_config.get('webhook_url'):
            self.channels['dingtalk'] = DingTalkNotifier(dingtalk_config)
            self.logger.debug("钉钉通知渠道初始化成功")
        
        # 邮件通知
        email_config = self.config_manager.get_notification_config().get('email', {})
        if email_config.get('smtp_server'):
            self.channels['email'] = EmailNotifier(email_config)
            self.logger.debug("邮件通知渠道初始化成功")
        
        # Webhook通知（预留）
        webhook_config = self.config_manager.get_notification_config().get('webhook', {})
        if webhook_config.get('url'):
            # self.channels['webhook'] = WebhookNotifier(webhook_config)
            self.logger.debug("Webhook通知渠道初始化成功")
    
    def notify_task_start(self, task_config: Dict[str, Any]):
        """通知任务开始"""
        self._notify_task_event(task_config, 'task_start')
    
    def notify_task_complete(self, task_config: Dict[str, Any], duration: float = None):
        """通知任务完成"""
        self._notify_task_event(task_config, 'task_complete', duration=duration)
    
    def notify_task_error(self, task_config: Dict[str, Any], error_message: str):
        """通知任务错误"""
        self._notify_task_event(task_config, 'task_error', error_message=error_message)
    
    def notify_review_required(self, task_config: Dict[str, Any]):
        """通知需要审查"""
        self._notify_task_event(task_config, 'review_required')
    
    def notify_review_complete(self, task_config: Dict[str, Any], issues_count: int = 0):
        """通知审查完成"""
        if issues_count > 0:
            self._notify_task_event(task_config, 'issues_found', issues_count=issues_count)
        else:
            self._notify_task_event(task_config, 'no_issues')
    
    def notify_critical_issue(self, task_config: Dict[str, Any], message: str):
        """通知关键问题"""
        self._notify_task_event(task_config, 'critical_issues', message=message)
    
    def _notify_task_event(self, task_config: Dict[str, Any], event_type: str, **kwargs):
        """
        通知任务事件
        
        Args:
            task_config: 任务配置
            event_type: 事件类型
            **kwargs: 其他参数
        """
        try:
            # 获取通知模板
            template = self.config_manager.get_notification_template(
                task_config.get('type', 'unknown'), 
                event_type
            )
            
            # 准备模板变量
            variables = self._prepare_template_variables(task_config, event_type, **kwargs)
            
            # 渲染消息
            message = self._render_template(template, variables)
            
            # 确定通知级别
            notification_level = self._get_notification_level(event_type)
            
            # 发送到各个渠道
            for channel_name, channel in self.channels.items():
                if self._should_notify(channel_name, notification_level):
                    try:
                        channel.send(message, notification_level, variables)
                        self.logger.info(f"通知发送成功: {channel_name} -> {event_type}")
                    except Exception as e:
                        self.logger.error(f"通知发送失败 {channel_name}: {e}")
            
        except Exception as e:
            self.logger.error(f"通知任务事件失败: {e}")
    
    def _prepare_template_variables(self, task_config: Dict[str, Any], 
                                  event_type: str, **kwargs) -> Dict[str, Any]:
        """
        准备模板变量
        
        Args:
            task_config: 任务配置
            event_type: 事件类型
            **kwargs: 其他参数
            
        Returns:
            模板变量字典
        """
        variables = {
            'task_name': task_config.get('name', 'Unknown Task'),
            'task_type': task_config.get('type', 'unknown'),
            'task_id': task_config.get('id', 'unknown'),
            'timestamp': datetime.now().isoformat(),
            'duration': self._format_duration(kwargs.get('duration', 0)),
            'error_message': kwargs.get('error_message', ''),
            'files_count': kwargs.get('files_count', 0),
            'issues_count': kwargs.get('issues_count', 0),
            'inconsistencies_count': kwargs.get('inconsistencies_count', 0),
            'output_path': kwargs.get('output_path', ''),
            'message': kwargs.get('message', '')
        }
        
        return variables
    
    def _render_template(self, template: str, variables: Dict[str, Any]) -> str:
        """
        渲染模板
        
        Args:
            template: 模板字符串
            variables: 变量字典
            
        Returns:
            渲染后的消息
        """
        try:
            message = template
            for key, value in variables.items():
                placeholder = f"{{{key}}}"
                if placeholder in message:
                    message = message.replace(placeholder, str(value))
            
            return message
        except Exception as e:
            self.logger.error(f"模板渲染失败: {e}")
            return template
    
    def _get_notification_level(self, event_type: str) -> str:
        """
        获取通知级别
        
        Args:
            event_type: 事件类型
            
        Returns:
            通知级别
        """
        notification_levels = self.config_manager.global_config.get(
            'notification_templates', {}).get('notification_levels', {})
        
        for level, event_types in notification_levels.items():
            if event_type in event_types:
                return level
        
        return 'info'
    
    def _should_notify(self, channel_name: str, notification_level: str) -> bool:
        """
        判断是否应该发送通知
        
        Args:
            channel_name: 渠道名称
            notification_level: 通知级别
            
        Returns:
            是否应该发送
        """
        # 这里可以根据渠道配置和通知级别进行过滤
        # 例如：某些渠道只接收错误级别的通知
        return True
    
    def _format_duration(self, duration_seconds: float) -> str:
        """
        格式化持续时间
        
        Args:
            duration_seconds: 持续时间（秒）
            
        Returns:
            格式化的时间字符串
        """
        if duration_seconds < 60:
            return f"{duration_seconds:.1f}秒"
        elif duration_seconds < 3600:
            minutes = duration_seconds / 60
            return f"{minutes:.1f}分钟"
        else:
            hours = duration_seconds / 3600
            return f"{hours:.1f}小时"


class DingTalkNotifier:
    """钉钉通知器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化钉钉通知器
        
        Args:
            config: 钉钉配置
        """
        self.webhook_url = config.get('webhook_url', '')
        self.secret = config.get('secret', '')
        self.at_users = config.get('at_users', [])
        self.at_all = config.get('at_all', False)
        self.logger = logging.getLogger(__name__)
    
    def send(self, message: str, level: str, variables: Dict[str, Any]):
        """
        发送钉钉通知
        
        Args:
            message: 消息内容
            level: 通知级别
            variables: 模板变量
        """
        try:
            # 构建钉钉消息
            dingtalk_message = self._build_dingtalk_message(message, level, variables)
            
            # 计算签名
            timestamp = str(round(time.time() * 1000))
            sign = self._calculate_sign(timestamp)
            
            # 发送请求
            url = f"{self.webhook_url}&timestamp={timestamp}&sign={sign}"
            response = requests.post(
                url,
                json=dingtalk_message,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('errcode') == 0:
                    self.logger.info("钉钉通知发送成功")
                else:
                    self.logger.error(f"钉钉通知发送失败: {result}")
            else:
                self.logger.error(f"钉钉通知HTTP请求失败: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"钉钉通知发送异常: {e}")
            raise
    
    def _build_dingtalk_message(self, message: str, level: str, 
                               variables: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建钉钉消息
        
        Args:
            message: 消息内容
            level: 通知级别
            variables: 模板变量
            
        Returns:
            钉钉消息字典
        """
        # 根据级别选择消息类型
        if level == 'error':
            title = f"❌ 任务执行失败: {variables.get('task_name', 'Unknown')}"
            color = "#FF0000"
        elif level == 'warning':
            title = f"⚠️ 任务需要关注: {variables.get('task_name', 'Unknown')}"
            color = "#FFA500"
        else:
            title = f"ℹ️ 任务状态更新: {variables.get('task_name', 'Unknown')}"
            color = "#00FF00"
        
        # 构建@用户列表
        at = {}
        if self.at_users:
            at['atMobiles'] = self.at_users
        if self.at_all:
            at['isAtAll'] = True
        
        # 构建消息内容
        content = f"""
{message}

**任务详情:**
- 任务名称: {variables.get('task_name', 'Unknown')}
- 任务类型: {variables.get('task_type', 'unknown')}
- 任务ID: {variables.get('task_id', 'unknown')}
- 执行时间: {variables.get('timestamp', 'unknown')}
"""
        
        if variables.get('duration'):
            content += f"- 执行耗时: {variables.get('duration')}\n"
        
        if variables.get('files_count'):
            content += f"- 生成文件数: {variables.get('files_count')}\n"
        
        if variables.get('issues_count'):
            content += f"- 发现问题数: {variables.get('issues_count')}\n"
        
        if variables.get('error_message'):
            content += f"- 错误信息: {variables.get('error_message')}\n"
        
        return {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": content
            },
            "at": at
        }
    
    def _calculate_sign(self, timestamp: str) -> str:
        """
        计算钉钉签名
        
        Args:
            timestamp: 时间戳
            
        Returns:
            签名字符串
        """
        if not self.secret:
            return ""
        
        string_to_sign = f"{timestamp}\n{self.secret}"
        hmac_code = hmac.new(
            self.secret.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        
        return base64.b64encode(hmac_code).decode('utf-8')


class EmailNotifier:
    """邮件通知器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化邮件通知器
        
        Args:
            config: 邮件配置
        """
        self.smtp_server = config.get('smtp_server', '')
        self.smtp_port = config.get('smtp_port', 587)
        self.username = config.get('username', '')
        self.password = config.get('password', '')
        self.from_email = config.get('from_email', self.username)
        self.to_emails = config.get('to_emails', [])
        self.use_tls = config.get('use_tls', True)
        self.use_ssl = config.get('use_ssl', False)
        self.logger = logging.getLogger(__name__)
    
    def send(self, message: str, level: str, variables: Dict[str, Any]):
        """
        发送邮件通知
        
        Args:
            message: 消息内容
            level: 通知级别
            variables: 模板变量
        """
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            from email.utils import formataddr
            
            # 构建邮件内容
            email_subject, email_body = self._build_email_content(message, level, variables)
            
            # 创建邮件对象
            msg = MIMEMultipart('alternative')
            msg['Subject'] = email_subject
            msg['From'] = formataddr(('Auto-Coder系统', self.from_email))
            msg['To'] = ', '.join(self.to_emails)
            
            # 添加HTML内容
            html_part = MIMEText(email_body, 'html', 'utf-8')
            msg.attach(html_part)
            
            # 添加纯文本内容
            text_part = MIMEText(self._strip_html(email_body), 'plain', 'utf-8')
            msg.attach(text_part)
            
            # 连接SMTP服务器
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                if self.use_tls:
                    server.starttls()
            
            # 登录
            if self.username and self.password:
                server.login(self.username, self.password)
            
            # 发送邮件
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"邮件通知发送成功: {', '.join(self.to_emails)}")
            
        except Exception as e:
            self.logger.error(f"邮件通知发送失败: {e}")
            raise
    
    def _build_email_content(self, message: str, level: str, variables: Dict[str, Any]) -> tuple:
        """
        构建邮件内容
        
        Returns:
            (subject, html_body)
        """
        # 根据级别设置主题前缀
        level_prefixes = {
            'info': '📢',
            'warning': '⚠️',
            'error': '🚨'
        }
        prefix = level_prefixes.get(level, '📢')
        
        # 构建主题
        subject = f"{prefix} Auto-Coder系统通知"
        
        # 构建HTML内容
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; }}
                .content {{ margin: 20px 0; }}
                .footer {{ color: #6c757d; font-size: 12px; margin-top: 30px; }}
                .level-info {{ color: #007bff; }}
                .level-warning {{ color: #ffc107; }}
                .level-error {{ color: #dc3545; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🤖 Auto-Coder系统通知</h2>
                <p>时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="content">
                <h3>消息内容:</h3>
                <p>{message}</p>
                
                <h3>详细信息:</h3>
                <ul>
                    <li><strong>通知级别:</strong> <span class="level-{level}">{level.upper()}</span></li>
                    <li><strong>任务ID:</strong> {variables.get('task_id', 'N/A')}</li>
                    <li><strong>任务类型:</strong> {variables.get('task_type', 'N/A')}</li>
                    <li><strong>执行时间:</strong> {variables.get('duration', 'N/A')}</li>
                </ul>
            </div>
            
            <div class="footer">
                <p>此邮件由Auto-Coder系统自动发送，请勿直接回复。</p>
                <p>如有问题，请联系系统管理员。</p>
            </div>
        </body>
        </html>
        """
        
        return subject, html_body
    
    def _strip_html(self, html_content: str) -> str:
        """去除HTML标签，获取纯文本内容"""
        import re
        # 简单的HTML标签去除
        text = re.sub(r'<[^>]+>', '', html_content)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()


class WebhookNotifier:
    """Webhook通知器（预留）"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def send(self, message: str, level: str, variables: Dict[str, Any]):
        """发送Webhook通知（预留实现）"""
        self.logger.info("Webhook通知功能暂未实现")
