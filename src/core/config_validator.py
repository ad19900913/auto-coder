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
    
"""
配置验证器 - 验证配置文件的完整性和有效性
"""

import logging
import re
import json
from typing import Dict, Any, List, Optional, Set, Tuple
from pathlib import Path
import yaml
from datetime import datetime
from urllib.parse import urlparse


class ConfigValidator:
    """配置验证器，验证配置文件的完整性和有效性"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.errors = []
        self.warnings = []
        self.validation_rules = {}
        self.custom_validators = {}
        
        # 初始化内置验证规则
        self._init_validation_rules()
    
    def _init_validation_rules(self):
        """初始化验证规则"""
        self.validation_rules = {
            'task_types': {
                'coding', 'review', 'doc', 'requirement_review', 'custom',
                'multimodal', 'ml_integration', 'smart_generation'
            },
            'schedule_types': {
                'cron', 'interval', 'once', 'manual'
            },
            'dependency_types': {
                'required', 'optional', 'conditional'
            },
            'resource_types': {
                'cpu', 'memory', 'disk', 'network', 'gpu'
            },
            'ai_service_types': {
                'openai', 'anthropic', 'google', 'azure', 'local'
            },
            'git_platforms': {
                'github', 'gitlab', 'bitbucket', 'gitee'
            },
            'notification_channels': {
                'email', 'slack', 'webhook', 'dingtalk', 'wechat'
            }
        }
    
    def add_custom_validator(self, name: str, validator_func):
        """
        添加自定义验证器
        
        Args:
            name: 验证器名称
            validator_func: 验证函数
        """
        self.custom_validators[name] = validator_func
        self.logger.info(f"添加自定义验证器: {name}")
    
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
        
        # 基础结构验证
        if not self._validate_config_structure(config, 'global'):
            return False
        
        # 验证必需字段
        required_fields = ['name', 'version', 'max_concurrent_tasks']
        for field in required_fields:
            if field not in config:
                self.errors.append(f"缺少必需字段: {field}")
        
        # 验证字段类型和值
        self._validate_field_types(config)
        self._validate_field_values(config)
        
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
        
        # 验证安全配置
        if 'security' in config:
            self._validate_security_config(config['security'])
        
        # 验证性能配置
        if 'performance' in config:
            self._validate_performance_config(config['performance'])
        
        # 执行自定义验证
        self._execute_custom_validators(config, 'global')
        
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
        
        # 基础结构验证
        if not self._validate_config_structure(config, 'task'):
            return False
        
        # 验证必需字段
        required_fields = ['name', 'type', 'enabled']
        for field in required_fields:
            if field not in config:
                self.errors.append(f"任务 {task_id} 缺少必需字段: {field}")
        
        # 验证字段类型和值
        self._validate_task_field_types(task_id, config)
        self._validate_task_field_values(task_id, config)
        
        # 验证任务类型
        task_type = config.get('type')
        if task_type and task_type not in self.validation_rules['task_types']:
            self.errors.append(f"任务 {task_id} 不支持的任务类型: {task_type}")
        
        # 验证调度配置
        if 'schedule' in config:
            self._validate_schedule_config(task_id, config['schedule'])
        
        # 验证依赖配置
        if 'dependencies' in config:
            self._validate_dependencies_config(task_id, config['dependencies'])
        
        # 验证资源需求
        if 'resource_requirements' in config:
            self._validate_resource_requirements(task_id, config['resource_requirements'])
        
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
        
        # 执行自定义验证
        self._execute_custom_validators(config, 'task')
        
        return len(self.errors) == 0
    
    def _validate_task_field_types(self, task_id: str, config: Dict[str, Any]):
        """验证任务字段类型"""
        type_rules = {
            'name': str,
            'description': str,
            'type': str,
            'enabled': bool,
            'priority': int
        }
        
        for field, expected_type in type_rules.items():
            if field in config and not isinstance(config[field], expected_type):
                self.errors.append(f"任务 {task_id} 字段 {field} 类型错误，期望 {expected_type.__name__}")
    
    def _validate_task_field_values(self, task_id: str, config: Dict[str, Any]):
        """验证任务字段值"""
        # 验证优先级
        if 'priority' in config:
            priority = config['priority']
            if not isinstance(priority, int):
                self.errors.append(f"任务 {task_id} 优先级必须是整数类型")
            elif priority < 1 or priority > 10:
                self.warnings.append(f"任务 {task_id} 优先级建议在1-10之间，当前值: {priority}")
        
        # 验证任务名称
        if 'name' in config:
            name = config['name']
            if not isinstance(name, str):
                self.errors.append(f"任务 {task_id} 名称必须是字符串类型")
            else:
                if len(name) > 100:
                    self.warnings.append(f"任务 {task_id} 名称过长，建议不超过100字符")
                if not re.match(r'^[a-zA-Z0-9_\-\u4e00-\u9fa5]+$', name):
                    self.warnings.append(f"任务 {task_id} 名称包含特殊字符，建议使用字母、数字、下划线、连字符或中文")
    
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
        
        if schedule_type not in self.validation_rules['schedule_types']:
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
    
    def _validate_config_structure(self, config: Dict[str, Any], config_type: str) -> bool:
        """验证配置结构"""
        if not isinstance(config, dict):
            self.errors.append(f"{config_type}配置必须是字典类型")
            return False
        
        # 检查是否有未知字段
        known_fields = self._get_known_fields(config_type)
        unknown_fields = set(config.keys()) - known_fields
        if unknown_fields:
            self.warnings.append(f"{config_type}配置包含未知字段: {unknown_fields}")
        
        return True
    
    def _get_known_fields(self, config_type: str) -> Set[str]:
        """获取已知字段列表"""
        field_maps = {
            'global': {
                'name', 'version', 'max_concurrent_tasks', 'ai_services', 'git',
                'notifications', 'coding_standards', 'security', 'performance'
            },
            'task': {
                'name', 'description', 'type', 'enabled', 'priority', 'schedule',
                'ai', 'git', 'notifications', 'retry', 'timeout', 'dependencies',
                'resource_requirements', 'parameters'
            }
        }
        return field_maps.get(config_type, set())
    
    def _validate_field_types(self, config: Dict[str, Any]):
        """验证字段类型"""
        type_rules = {
            'name': str,
            'version': str,
            'max_concurrent_tasks': int,
            'enabled': bool,
            'priority': int
        }
        
        for field, expected_type in type_rules.items():
            if field in config and not isinstance(config[field], expected_type):
                self.errors.append(f"字段 {field} 类型错误，期望 {expected_type.__name__}")
    
    def _validate_field_values(self, config: Dict[str, Any]):
        """验证字段值"""
        # 验证版本号格式
        if 'version' in config:
            version = config['version']
            if not re.match(r'^\d+\.\d+\.\d+', version):
                self.warnings.append(f"版本号格式建议使用语义化版本: {version}")
        
        # 验证并发任务数
        if 'max_concurrent_tasks' in config:
            max_tasks = config['max_concurrent_tasks']
            if max_tasks <= 0:
                self.errors.append("最大并发任务数必须大于0")
            elif max_tasks > 100:
                self.warnings.append("最大并发任务数过大，可能影响性能")
    
    def _validate_security_config(self, config: Dict[str, Any]):
        """验证安全配置"""
        if not isinstance(config, dict):
            self.errors.append("安全配置必须是字典类型")
            return
        
        # 验证加密配置
        if 'encryption' in config:
            encryption_config = config['encryption']
            if not isinstance(encryption_config, dict):
                self.errors.append("加密配置必须是字典类型")
            else:
                # 验证加密算法
                algorithm = encryption_config.get('algorithm')
                if algorithm and algorithm not in ['AES', 'RSA', 'ChaCha20']:
                    self.warnings.append(f"不常见的加密算法: {algorithm}")
        
        # 验证访问控制
        if 'access_control' in config:
            access_config = config['access_control']
            if not isinstance(access_config, dict):
                self.errors.append("访问控制配置必须是字典类型")
            else:
                # 验证IP白名单
                ip_whitelist = access_config.get('ip_whitelist', [])
                if not isinstance(ip_whitelist, list):
                    self.errors.append("IP白名单必须是列表类型")
                else:
                    for ip in ip_whitelist:
                        if not self._is_valid_ip(ip):
                            self.warnings.append(f"无效的IP地址: {ip}")
    
    def _validate_performance_config(self, config: Dict[str, Any]):
        """验证性能配置"""
        if not isinstance(config, dict):
            self.errors.append("性能配置必须是字典类型")
            return
        
        # 验证缓存配置
        if 'cache' in config:
            cache_config = config['cache']
            if not isinstance(cache_config, dict):
                self.errors.append("缓存配置必须是字典类型")
            else:
                # 验证缓存大小
                max_size = cache_config.get('max_size')
                if max_size is not None and (not isinstance(max_size, int) or max_size <= 0):
                    self.errors.append("缓存最大大小必须为正整数")
                
                # 验证TTL
                ttl = cache_config.get('ttl')
                if ttl is not None and (not isinstance(ttl, int) or ttl <= 0):
                    self.errors.append("缓存TTL必须为正整数")
        
        # 验证连接池配置
        if 'connection_pool' in config:
            pool_config = config['connection_pool']
            if not isinstance(pool_config, dict):
                self.errors.append("连接池配置必须是字典类型")
            else:
                # 验证连接数
                max_connections = pool_config.get('max_connections')
                if max_connections is not None and (not isinstance(max_connections, int) or max_connections <= 0):
                    self.errors.append("最大连接数必须为正整数")
    
    def _validate_dependencies_config(self, task_id: str, dependencies: List[Dict[str, Any]]):
        """验证依赖配置"""
        if not isinstance(dependencies, list):
            self.errors.append(f"任务 {task_id} 依赖配置必须是列表类型")
            return
        
        for i, dep in enumerate(dependencies):
            if not isinstance(dep, dict):
                self.errors.append(f"任务 {task_id} 依赖[{i}]必须是字典类型")
                continue
            
            # 验证必需字段
            if 'task_id' not in dep:
                self.errors.append(f"任务 {task_id} 依赖[{i}]缺少task_id字段")
            
            # 验证依赖类型
            dep_type = dep.get('type', 'required')
            if dep_type not in self.validation_rules['dependency_types']:
                self.errors.append(f"任务 {task_id} 依赖[{i}]无效的依赖类型: {dep_type}")
            
            # 验证超时设置
            timeout = dep.get('timeout')
            if timeout is not None and (not isinstance(timeout, int) or timeout <= 0):
                self.errors.append(f"任务 {task_id} 依赖[{i}]超时必须为正整数")
    
    def _validate_resource_requirements(self, task_id: str, requirements: Dict[str, Any]):
        """验证资源需求配置"""
        if not isinstance(requirements, dict):
            self.errors.append(f"任务 {task_id} 资源需求必须是字典类型")
            return
        
        for resource_type, amount in requirements.items():
            # 验证资源类型
            if resource_type not in self.validation_rules['resource_types']:
                self.warnings.append(f"任务 {task_id} 未知的资源类型: {resource_type}")
            
            # 验证资源数量
            if not isinstance(amount, (int, float)) or amount <= 0:
                self.errors.append(f"任务 {task_id} 资源 {resource_type} 数量必须为正数")
            
            # 验证资源上限
            if resource_type == 'cpu' and amount > 100:
                self.warnings.append(f"任务 {task_id} CPU使用率超过100%: {amount}%")
            elif resource_type == 'memory' and amount > 32768:
                self.warnings.append(f"任务 {task_id} 内存需求过大: {amount}MB")
    
    def _is_valid_ip(self, ip: str) -> bool:
        """验证IP地址格式"""
        try:
            parts = ip.split('.')
            if len(parts) != 4:
                return False
            for part in parts:
                if not part.isdigit() or not 0 <= int(part) <= 255:
                    return False
            return True
        except Exception:
            return False
    
    def _is_valid_url(self, url: str) -> bool:
        """验证URL格式"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def _execute_custom_validators(self, config: Dict[str, Any], config_type: str):
        """执行自定义验证器"""
        for name, validator_func in self.custom_validators.items():
            try:
                result = validator_func(config, config_type)
                if result is False:
                    self.errors.append(f"自定义验证器 {name} 验证失败")
                elif isinstance(result, str):
                    self.errors.append(f"自定义验证器 {name}: {result}")
            except Exception as e:
                self.errors.append(f"自定义验证器 {name} 执行异常: {e}")
    
    def validate_config_file(self, file_path: str) -> Tuple[bool, Dict[str, Any]]:
        """
        验证配置文件
        
        Args:
            file_path: 配置文件路径
            
        Returns:
            (是否验证通过, 配置内容)
        """
        try:
            # 检查文件是否存在
            if not Path(file_path).exists():
                self.errors.append(f"配置文件不存在: {file_path}")
                return False, {}
            
            # 检查文件扩展名
            if not file_path.endswith(('.yaml', '.yml', '.json')):
                self.warnings.append(f"配置文件扩展名建议使用.yaml或.json: {file_path}")
            
            # 读取配置文件
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.endswith('.json'):
                    config = json.load(f)
                else:
                    config = yaml.safe_load(f)
            
            # 验证配置内容
            if file_path.endswith('global_config.yaml'):
                is_valid = self.validate_global_config(config)
            else:
                is_valid = self.validate_task_config('unknown', config)
            
            return is_valid, config
            
        except yaml.YAMLError as e:
            self.errors.append(f"YAML格式错误: {e}")
            return False, {}
        except json.JSONDecodeError as e:
            self.errors.append(f"JSON格式错误: {e}")
            return False, {}
        except Exception as e:
            self.errors.append(f"读取配置文件失败: {e}")
            return False, {}
    
    def generate_validation_report(self) -> Dict[str, Any]:
        """生成验证报告"""
        return {
            'timestamp': datetime.now().isoformat(),
            'valid': len(self.errors) == 0,
            'error_count': len(self.errors),
            'warning_count': len(self.warnings),
            'errors': self.errors.copy(),
            'warnings': self.warnings.copy(),
            'summary': {
                'total_issues': len(self.errors) + len(self.warnings),
                'critical_issues': len(self.errors),
                'suggestions': len(self.warnings)
            }
        }
    
    def has_warnings(self) -> bool:
        """是否有验证警告"""
        return len(self.warnings) > 0
