"""
配置验证器 - 验证配置文件的完整性和有效性
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import yaml


class ConfigValidator:
    """配置验证器，验证配置文件的完整性和有效性"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.errors = []
        self.warnings = []
    
    def validate_global_config(self, config: Dict[str, Any]) -> bool:
        """
        验证全局配置
        
        Args:
            config: 全局配置字典
            
        Returns:
            是否验证通过
        """
        self.errors.clear()
        self.warnings.clear()
        
        # 验证必需字段
        required_fields = ['name', 'version', 'max_concurrent_tasks']
        for field in required_fields:
            if field not in config:
                self.errors.append(f"缺少必需字段: {field}")
        
        # 验证AI服务配置
        if 'ai_services' in config:
            self._validate_ai_services_config(config['ai_services'])
        
        # 验证Git配置
        if 'git' in config:
            self._validate_git_config(config['git'])
        
        # 验证通知配置
        if 'notifications' in config:
            self._validate_notification_config(config['notifications'])
        
        # 验证编码规范配置
        if 'coding_standards' in config:
            self._validate_coding_standards_config(config['coding_standards'])
        
        return len(self.errors) == 0
    
    def validate_task_config(self, task_id: str, config: Dict[str, Any]) -> bool:
        """
        验证任务配置
        
        Args:
            task_id: 任务ID
            config: 任务配置字典
            
        Returns:
            是否验证通过
        """
        self.errors.clear()
        self.warnings.clear()
        
        # 验证必需字段
        required_fields = ['name', 'type', 'enabled']
        for field in required_fields:
            if field not in config:
                self.errors.append(f"任务 {task_id} 缺少必需字段: {field}")
        
        # 验证任务类型
        valid_types = ['coding', 'review', 'doc', 'requirement_review', 'custom']
        task_type = config.get('type')
        if task_type and task_type not in valid_types:
            self.errors.append(f"任务 {task_id} 不支持的任务类型: {task_type}")
        
        # 验证调度配置
        if 'schedule' in config:
            self._validate_schedule_config(task_id, config['schedule'])
        
        # 验证AI配置
        if 'ai' in config:
            self._validate_task_ai_config(task_id, config['ai'])
        
        # 验证Git配置
        if 'git' in config:
            self._validate_task_git_config(task_id, config['git'])
        
        # 验证通知配置
        if 'notifications' in config:
            self._validate_task_notification_config(task_id, config['notifications'])
        
        # 验证重试配置
        if 'retry' in config:
            self._validate_retry_config(task_id, config['retry'])
        
        # 验证超时配置
        if 'timeout' in config:
            self._validate_timeout_config(task_id, config['timeout'])
        
        return len(self.errors) == 0
    
    def _validate_ai_services_config(self, config: Dict[str, Any]):
        """验证AI服务配置"""
        if not isinstance(config, dict):
            self.errors.append("AI服务配置必须是字典类型")
            return
        
        # 验证默认服务
        default_service = config.get('default')
        if default_service and default_service not in config:
            self.errors.append(f"默认AI服务不存在: {default_service}")
        
        # 验证各个服务配置
        for service_name, service_config in config.items():
            if service_name == 'default':
                continue
            
            if not isinstance(service_config, dict):
                self.errors.append(f"AI服务 {service_name} 配置必须是字典类型")
                continue
            
            # 验证API密钥
            if 'api_key' not in service_config:
                self.errors.append(f"AI服务 {service_name} 缺少API密钥")
            
            # 验证模型配置
            if 'model' not in service_config:
                self.warnings.append(f"AI服务 {service_name} 缺少模型配置")
    
    def _validate_git_config(self, config: Dict[str, Any]):
        """验证Git配置"""
        if not isinstance(config, dict):
            self.errors.append("Git配置必须是字典类型")
            return
        
        # 验证默认平台
        default_platform = config.get('default')
        if default_platform and default_platform not in config:
            self.errors.append(f"默认Git平台不存在: {default_platform}")
        
        # 验证各个平台配置
        for platform_name, platform_config in config.items():
            if platform_name == 'default':
                continue
            
            if not isinstance(platform_config, dict):
                self.errors.append(f"Git平台 {platform_name} 配置必须是字典类型")
                continue
            
            # 验证访问令牌
            if 'token' not in platform_config:
                self.errors.append(f"Git平台 {platform_name} 缺少访问令牌")
            
            # 验证用户名
            if 'username' not in platform_config:
                self.warnings.append(f"Git平台 {platform_name} 缺少用户名配置")
    
    def _validate_notification_config(self, config: Dict[str, Any]):
        """验证通知配置"""
        if not isinstance(config, dict):
            self.errors.append("通知配置必须是字典类型")
            return
        
        # 验证通知渠道
        channels = config.get('channels', {})
        for channel_name, channel_config in channels.items():
            if not isinstance(channel_config, dict):
                self.errors.append(f"通知渠道 {channel_name} 配置必须是字典类型")
                continue
            
            # 验证渠道类型
            channel_type = channel_config.get('type')
            if not channel_type:
                self.errors.append(f"通知渠道 {channel_name} 缺少类型配置")
    
    def _validate_coding_standards_config(self, config: Dict[str, Any]):
        """验证编码规范配置"""
        if not isinstance(config, dict):
            self.errors.append("编码规范配置必须是字典类型")
            return
        
        for language, language_config in config.items():
            if not isinstance(language_config, dict):
                self.errors.append(f"语言 {language} 配置必须是字典类型")
                continue
            
            # 验证文件路径
            file_path = language_config.get('file_path')
            if file_path and not Path(file_path).exists():
                self.warnings.append(f"编码规范文件不存在: {file_path}")
    
    def _validate_schedule_config(self, task_id: str, config: Dict[str, Any]):
        """验证调度配置"""
        if not isinstance(config, dict):
            self.errors.append(f"任务 {task_id} 调度配置必须是字典类型")
            return
        
        # 验证调度类型
        schedule_type = config.get('type')
        if not schedule_type:
            self.errors.append(f"任务 {task_id} 缺少调度类型")
            return
        
        valid_types = ['cron', 'interval', 'date']
        if schedule_type not in valid_types:
            self.errors.append(f"任务 {task_id} 不支持的调度类型: {schedule_type}")
            return
        
        # 验证cron表达式
        if schedule_type == 'cron':
            # 检查新的cron_expressions格式（优先）
            cron_expressions = config.get('cron_expressions', [])
            if cron_expressions:
                # 验证每个cron表达式
                for i, expr in enumerate(cron_expressions):
                    if not self._is_valid_cron_expression(expr):
                        self.errors.append(f"任务 {task_id} cron表达式[{i}]无效: {expr}")
            else:
                # 检查旧的expression字段格式（向后兼容）
                expression = config.get('expression')
                if not expression:
                    self.errors.append(f"任务 {task_id} cron调度缺少表达式")
                elif not self._is_valid_cron_expression(expression):
                    self.errors.append(f"任务 {task_id} cron表达式无效: {expression}")
    
    def _validate_task_ai_config(self, task_id: str, config: Dict[str, Any]):
        """验证任务AI配置"""
        if not isinstance(config, dict):
            self.errors.append(f"任务 {task_id} AI配置必须是字典类型")
            return
        
        # 验证提供商
        provider = config.get('provider')
        if provider and provider not in ['claude', 'deepseek']:
            self.errors.append(f"任务 {task_id} 不支持的AI提供商: {provider}")
    
    def _validate_task_git_config(self, task_id: str, config: Dict[str, Any]):
        """验证任务Git配置"""
        if not isinstance(config, dict):
            self.errors.append(f"任务 {task_id} Git配置必须是字典类型")
            return
        
        # 验证平台
        platform = config.get('platform')
        if platform and platform not in ['github', 'gitlab']:
            self.errors.append(f"任务 {task_id} 不支持的Git平台: {platform}")
    
    def _validate_task_notification_config(self, task_id: str, config: Dict[str, Any]):
        """验证任务通知配置"""
        if not isinstance(config, dict):
            self.errors.append(f"任务 {task_id} 通知配置必须是字典类型")
            return
        
        # 验证事件列表
        events = config.get('events', [])
        if not isinstance(events, list):
            self.errors.append(f"任务 {task_id} 通知事件必须是列表类型")
    
    def _validate_retry_config(self, task_id: str, config: Dict[str, Any]):
        """验证重试配置"""
        if not isinstance(config, dict):
            self.errors.append(f"任务 {task_id} 重试配置必须是字典类型")
            return
        
        # 验证最大重试次数
        max_attempts = config.get('max_attempts')
        if max_attempts is not None and (not isinstance(max_attempts, int) or max_attempts < 0):
            self.errors.append(f"任务 {task_id} 最大重试次数必须是正整数")
    
    def _validate_timeout_config(self, task_id: str, config: Dict[str, Any]):
        """验证超时配置"""
        if not isinstance(config, dict):
            self.errors.append(f"任务 {task_id} 超时配置必须是字典类型")
            return
        
        # 验证任务超时
        task_timeout = config.get('task')
        if task_timeout is not None and (not isinstance(task_timeout, int) or task_timeout <= 0):
            self.errors.append(f"任务 {task_id} 任务超时必须为正整数")
    
    def _is_valid_cron_expression(self, expression: str) -> bool:
        """验证cron表达式"""
        try:
            # 简单的cron表达式验证
            parts = expression.split()
            if len(parts) != 5:
                return False
            
            # 验证每个字段的范围
            minute, hour, day, month, weekday = parts
            
            # 这里可以添加更详细的验证逻辑
            # 暂时只检查基本格式
            
            return True
        except Exception:
            return False
    
    def get_errors(self) -> List[str]:
        """获取验证错误"""
        return self.errors.copy()
    
    def get_warnings(self) -> List[str]:
        """获取验证警告"""
        return self.warnings.copy()
    
    def has_errors(self) -> bool:
        """是否有验证错误"""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """是否有验证警告"""
        return len(self.warnings) > 0
