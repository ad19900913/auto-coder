"""
配置管理器 - 管理全局和任务级配置
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime


class ConfigManager:
    """配置管理器，管理全局和任务级配置"""
    
    def __init__(self, config_dir: str = "./config"):
        """
        初始化配置管理器
        
        Args:
            config_dir: 配置文件目录路径
        """
        self.config_dir = Path(config_dir)
        self.global_config = {}
        self.coding_standards = {}
        self.task_configs = {}
        self.logger = logging.getLogger(__name__)
        
        # 加载配置
        self._load_configs()
    
    def _load_configs(self):
        """加载所有配置文件"""
        try:
            # 加载全局配置
            self._load_global_config()
            
            # 加载编码规范
            self._load_coding_standards()
            
            # 加载任务配置
            self._load_task_configs()
            
            self.logger.info("配置加载完成")
        except Exception as e:
            self.logger.error(f"配置加载失败: {e}")
            raise
    
    def _load_global_config(self):
        """加载全局配置文件"""
        global_config_path = self.config_dir / "global_config.yaml"
        
        if not global_config_path.exists():
            self.logger.warning(f"全局配置文件不存在: {global_config_path}")
            self.global_config = self._get_default_global_config()
            return
        
        try:
            with open(global_config_path, 'r', encoding='utf-8') as f:
                self.global_config = yaml.safe_load(f)
            
            # 处理环境变量
            self._process_environment_variables()
            
            self.logger.info("全局配置加载成功")
        except Exception as e:
            self.logger.error(f"全局配置加载失败: {e}")
            self.global_config = self._get_default_global_config()
    
    def _load_coding_standards(self):
        """加载编码规范文件"""
        coding_standards_config = self.global_config.get('coding_standards', {})
        
        for language, config in coding_standards_config.items():
            if not config.get('enabled', False):
                continue
            
            file_path = config.get('file_path')
            if not file_path:
                continue
            
            try:
                standards_path = Path(file_path)
                if standards_path.exists():
                    with open(standards_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        self.coding_standards[language] = {
                            'content': content,
                            'config': config,
                            'last_modified': standards_path.stat().st_mtime
                        }
                    self.logger.info(f"编码规范加载成功: {language}")
                else:
                    self.logger.warning(f"编码规范文件不存在: {standards_path}")
            except Exception as e:
                self.logger.error(f"编码规范加载失败 {language}: {e}")
    
    def _load_task_configs(self):
        """加载任务配置文件"""
        tasks_dir = self.config_dir / "tasks"
        if not tasks_dir.exists():
            self.logger.info("任务配置目录不存在，跳过加载")
            return
        
        for task_file in tasks_dir.glob("*.yaml"):
            try:
                with open(task_file, 'r', encoding='utf-8') as f:
                    task_config = yaml.safe_load(f)
                    task_name = task_file.stem
                    self.task_configs[task_name] = task_config
                self.logger.info(f"任务配置加载成功: {task_name}")
            except Exception as e:
                self.logger.error(f"任务配置加载失败 {task_file}: {e}")
    
    def _process_environment_variables(self):
        """处理环境变量替换"""
        def replace_env_vars(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    obj[key] = replace_env_vars(value)
            elif isinstance(obj, list):
                for i, value in enumerate(obj):
                    obj[i] = replace_env_vars(value)
            elif isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
                env_var = obj[2:-1]
                return os.getenv(env_var, obj)
            return obj
        
        self.global_config = replace_env_vars(self.global_config)
    
    def _get_default_global_config(self) -> Dict[str, Any]:
        """获取默认全局配置"""
        return {
            'ai_services': {
                'claude': {
                    'api_key': '',
                    'base_url': 'https://api.anthropic.com',
                    'model': 'claude-3-sonnet-20240229',
                    'max_tokens': 4000,
                    'temperature': 0.1
                }
            },
            'git': {
                'github': {'token': '', 'username': ''},
                'gitlab': {'token': '', 'base_url': ''}
            },
            'notification': {
                'dingtalk': {'webhook_url': '', 'secret': '', 'at_users': []}
            },
            'logging': {'level': 'INFO', 'retention_days': 30},
            'system': {
                'work_dir': './states',
                'output_dir': './outputs',
                'max_concurrent_tasks': 5,
                'default_timeout': 300
            }
        }
    
    def get_coding_standards(self, language: Optional[str] = None) -> Dict[str, Any]:
        """
        获取编码规范
        
        Args:
            language: 编程语言，如果为None则返回所有规范
            
        Returns:
            编码规范字典
        """
        if language is None:
            return self.coding_standards
        
        return self.coding_standards.get(language, {})
    
    def get_task_timeout(self, task_type: str) -> int:
        """
        获取任务超时时间
        
        Args:
            task_type: 任务类型
            
        Returns:
            超时时间（秒）
        """
        timeouts = self.global_config.get('task_timeouts', {})
        return timeouts.get(task_type, timeouts.get('global', {}).get('default', 300))
    
    def get_retry_config(self, task_type: Optional[str] = None) -> Dict[str, Any]:
        """
        获取重试配置
        
        Args:
            task_type: 任务类型，如果为None则返回全局配置
            
        Returns:
            重试配置字典
        """
        retry_config = self.global_config.get('retry_config', {})
        
        if task_type is None:
            return retry_config
        
        # 合并全局配置和任务特定配置
        task_specific = retry_config.get('task_specific', {}).get(task_type, {})
        result = retry_config.copy()
        result.update(task_specific)
        
        return result
    
    def get_ai_parameters(self, model: str, task_type: str) -> Dict[str, Any]:
        """
        获取AI模型参数
        
        Args:
            model: AI模型名称（claude, deepseek）
            task_type: 任务类型
            
        Returns:
            AI参数字典
        """
        ai_services = self.global_config.get('ai_services', {})
        model_config = ai_services.get(model, {})
        
        if not model_config:
            return {}
        
        # 基础参数
        parameters = model_config.get('parameters', {}).copy()
        
        # 任务特定参数
        task_parameters = model_config.get('task_parameters', {}).get(task_type, {})
        parameters.update(task_parameters)
        
        return parameters
    
    def get_notification_template(self, task_type: str, event_type: str) -> str:
        """
        获取通知模板
        
        Args:
            task_type: 任务类型
            event_type: 事件类型
            
        Returns:
            通知模板字符串
        """
        templates = self.global_config.get('notification_templates', {})
        
        # 优先获取任务特定模板
        task_templates = templates.get('task_specific', {}).get(task_type, {})
        if event_type in task_templates:
            return task_templates[event_type]
        
        # 回退到通用模板
        common_templates = templates.get('common', {})
        return common_templates.get(event_type, f"任务事件: {event_type}")
    
    def get_ai_service_config(self, service_name: str) -> Dict[str, Any]:
        """
        获取AI服务配置
        
        Args:
            service_name: 服务名称（claude, deepseek）
            
        Returns:
            AI服务配置字典
        """
        return self.global_config.get('ai_services', {}).get(service_name, {})
    
    def get_git_config(self, platform: str) -> Dict[str, Any]:
        """
        获取Git平台配置
        
        Args:
            platform: Git平台（github, gitlab）
            
        Returns:
            Git配置字典
        """
        return self.global_config.get('git', {}).get(platform, {})
    
    def get_notification_config(self) -> Dict[str, Any]:
        """获取通知配置"""
        return self.global_config.get('notification', {})
    
    def get_system_config(self) -> Dict[str, Any]:
        """获取系统配置"""
        return self.global_config.get('system', {})
    
    def get_state_management_config(self) -> Dict[str, Any]:
        """获取状态管理配置"""
        return self.global_config.get('state_management', {})
    
    def reload_configs(self):
        """重新加载所有配置"""
        self.logger.info("重新加载配置...")
        self._load_configs()
    
    def reload_coding_standards(self):
        """重新加载编码规范"""
        self.logger.info("重新加载编码规范...")
        self._load_coding_standards()
    
    def get_config_summary(self) -> Dict[str, Any]:
        """获取配置摘要信息"""
        return {
            'config_dir': str(self.config_dir),
            'global_config_loaded': bool(self.global_config),
            'coding_standards_count': len(self.coding_standards),
            'task_configs_count': len(self.task_configs),
            'ai_services': list(self.global_config.get('ai_services', {}).keys()),
            'last_updated': datetime.now().isoformat()
        }
