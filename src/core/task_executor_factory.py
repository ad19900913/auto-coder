"""
任务执行器工厂 - 根据任务类型创建对应的执行器实例
"""

import logging
from typing import Dict, Any, Type
from .task_executor import TaskExecutor
from .config_manager import ConfigManager
from .state_manager import StateManager
from ..services.notify_service import NotifyService


class TaskExecutorFactory:
    """任务执行器工厂类"""
    
    def __init__(self, config_manager: ConfigManager, state_manager: StateManager, 
                 notify_service: NotifyService):
        """
        初始化任务执行器工厂
        
        Args:
            config_manager: 配置管理器
            state_manager: 状态管理器
            notify_service: 通知服务
        """
        self.config_manager = config_manager
        self.state_manager = state_manager
        self.notify_service = notify_service
        self.logger = logging.getLogger(__name__)
        
        # 注册任务类型与执行器的映射
        self._executor_registry = {}
        self._register_executors()
    
    def _register_executors(self):
        """注册所有可用的任务执行器"""
        try:
            # 动态导入任务执行器模块
            from ..tasks.coding_executor import CodingTaskExecutor
            from ..tasks.review_executor import ReviewTaskExecutor
            from ..tasks.doc_executor import DocTaskExecutor
            from ..tasks.requirement_review_executor import RequirementReviewTaskExecutor
            from ..tasks.custom_executor import CustomTaskExecutor
            
            # 注册执行器
            self._executor_registry = {
                'coding': CodingTaskExecutor,
                'review': ReviewTaskExecutor,
                'doc': DocTaskExecutor,
                'requirement_review': RequirementReviewTaskExecutor,
                'custom': CustomTaskExecutor
            }
            
            self.logger.info(f"任务执行器注册完成，支持的任务类型: {list(self._executor_registry.keys())}")
            
        except ImportError as e:
            self.logger.warning(f"部分任务执行器导入失败: {e}")
            # 继续注册可用的执行器
            pass
        except Exception as e:
            self.logger.error(f"注册任务执行器失败: {e}")
            raise
    
    def create_executor(self, task_id: str, task_type: str = None) -> TaskExecutor:
        """
        创建任务执行器实例
        
        Args:
            task_id: 任务ID
            task_type: 任务类型，如果为None则从配置中获取
            
        Returns:
            任务执行器实例
            
        Raises:
            ValueError: 不支持的任务类型
            RuntimeError: 执行器创建失败
        """
        try:
            # 如果没有指定任务类型，从配置中获取
            if not task_type:
                task_config = self.config_manager.get_task_config(task_id)
                if not task_config:
                    raise ValueError(f"任务配置不存在: {task_id}")
                task_type = task_config.get('type')
            
            if not task_type:
                raise ValueError(f"任务类型未指定: {task_id}")
            
            # 检查任务类型是否支持
            if task_type not in self._executor_registry:
                supported_types = list(self._executor_registry.keys())
                raise ValueError(f"不支持的任务类型: {task_type}，支持的类型: {supported_types}")
            
            # 获取执行器类
            executor_class = self._executor_registry[task_type]
            
            # 创建执行器实例
            executor = executor_class(
                task_id=task_id,
                config_manager=self.config_manager,
                state_manager=self.state_manager,
                notify_service=self.notify_service
            )
            
            self.logger.info(f"任务执行器创建成功: {task_id} -> {task_type}")
            return executor
            
        except ValueError as e:
            # 重新抛出ValueError
            raise
        except Exception as e:
            self.logger.error(f"创建任务执行器失败 {task_id}: {e}")
            raise RuntimeError(f"创建任务执行器失败: {e}")
    
    def get_supported_task_types(self) -> list:
        """
        获取支持的任务类型列表
        
        Returns:
            支持的任务类型列表
        """
        return list(self._executor_registry.keys())
    
    def is_task_type_supported(self, task_type: str) -> bool:
        """
        检查任务类型是否支持
        
        Args:
            task_type: 任务类型
            
        Returns:
            是否支持
        """
        return task_type in self._executor_registry
    
    def get_executor_class(self, task_type: str) -> Type[TaskExecutor]:
        """
        获取指定任务类型的执行器类
        
        Args:
            task_type: 任务类型
            
        Returns:
            执行器类
            
        Raises:
            ValueError: 不支持的任务类型
        """
        if task_type not in self._executor_registry:
            supported_types = list(self._executor_registry.keys())
            raise ValueError(f"不支持的任务类型: {task_type}，支持的类型: {supported_types}")
        
        return self._executor_registry[task_type]
    
    def register_executor(self, task_type: str, executor_class: Type[TaskExecutor]):
        """
        注册新的任务执行器
        
        Args:
            task_type: 任务类型
            executor_class: 执行器类
            
        Raises:
            ValueError: 执行器类无效
        """
        try:
            # 验证执行器类
            if not issubclass(executor_class, TaskExecutor):
                raise ValueError(f"执行器类必须继承自TaskExecutor: {executor_class}")
            
            # 注册执行器
            self._executor_registry[task_type] = executor_class
            
            self.logger.info(f"新任务执行器注册成功: {task_type} -> {executor_class.__name__}")
            
        except Exception as e:
            self.logger.error(f"注册任务执行器失败 {task_type}: {e}")
            raise
    
    def unregister_executor(self, task_type: str) -> bool:
        """
        注销任务执行器
        
        Args:
            task_type: 任务类型
            
        Returns:
            是否注销成功
        """
        try:
            if task_type in self._executor_registry:
                executor_class = self._executor_registry.pop(task_type)
                self.logger.info(f"任务执行器注销成功: {task_type} -> {executor_class.__name__}")
                return True
            else:
                self.logger.warning(f"任务执行器不存在: {task_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"注销任务执行器失败 {task_type}: {e}")
            return False
    
    def get_executor_info(self) -> Dict[str, Any]:
        """
        获取所有执行器的信息
        
        Returns:
            执行器信息字典
        """
        try:
            executor_info = {}
            
            for task_type, executor_class in self._executor_registry.items():
                executor_info[task_type] = {
                    'class_name': executor_class.__name__,
                    'module': executor_class.__module__,
                    'description': getattr(executor_class, '__doc__', '无描述'),
                    'supported_features': self._get_executor_features(executor_class)
                }
            
            return executor_info
            
        except Exception as e:
            self.logger.error(f"获取执行器信息失败: {e}")
            return {}
    
    def _get_executor_features(self, executor_class: Type[TaskExecutor]) -> list:
        """
        获取执行器支持的功能特性
        
        Args:
            executor_class: 执行器类
            
        Returns:
            功能特性列表
        """
        try:
            features = []
            
            # 检查是否支持AI服务
            if hasattr(executor_class, 'ai_service'):
                features.append('ai_service')
            
            # 检查是否支持Git服务
            if hasattr(executor_class, 'git_service'):
                features.append('git_service')
            
            # 检查是否支持进度更新
            if hasattr(executor_class, '_update_progress'):
                features.append('progress_tracking')
            
            # 检查是否支持元数据管理
            if hasattr(executor_class, '_add_metadata'):
                features.append('metadata_management')
            
            # 检查是否支持输出保存
            if hasattr(executor_class, '_save_output'):
                features.append('output_saving')
            
            # 检查是否支持重试机制
            if hasattr(executor_class, '_should_retry'):
                features.append('retry_mechanism')
            
            return features
            
        except Exception as e:
            self.logger.warning(f"获取执行器特性失败: {e}")
            return []
    
    def validate_task_config(self, task_id: str, task_config: Dict[str, Any]) -> list:
        """
        验证任务配置的有效性
        
        Args:
            task_id: 任务ID
            task_config: 任务配置
            
        Returns:
            验证错误列表，空列表表示配置有效
        """
        try:
            errors = []
            
            # 检查必需字段
            required_fields = ['type', 'schedule']
            for field in required_fields:
                if field not in task_config:
                    errors.append(f"缺少必需字段: {field}")
            
            # 检查任务类型
            task_type = task_config.get('type')
            if task_type and not self.is_task_type_supported(task_type):
                supported_types = self.get_supported_task_types()
                errors.append(f"不支持的任务类型: {task_type}，支持的类型: {supported_types}")
            
            # 检查调度配置
            schedule_config = task_config.get('schedule', {})
            if schedule_config:
                schedule_errors = self._validate_schedule_config(schedule_config)
                errors.extend(schedule_errors)
            
            # 检查AI配置
            ai_config = task_config.get('ai', {})
            if ai_config:
                ai_errors = self._validate_ai_config(ai_config)
                errors.extend(ai_errors)
            
            # 检查Git配置
            git_config = task_config.get('git', {})
            if git_config:
                git_errors = self._validate_git_config(git_config)
                errors.extend(git_errors)
            
            return errors
            
        except Exception as e:
            self.logger.error(f"验证任务配置失败: {e}")
            return [f"配置验证异常: {e}"]
    
    def _validate_schedule_config(self, schedule_config: Dict[str, Any]) -> list:
        """
        验证调度配置
        
        Args:
            schedule_config: 调度配置
            
        Returns:
            验证错误列表
        """
        errors = []
        
        schedule_type = schedule_config.get('type', 'cron')
        
        if schedule_type == 'cron':
            # 验证cron配置
            cron_config = schedule_config.get('cron', {})
            if not cron_config:
                errors.append("cron类型调度缺少cron配置")
        
        elif schedule_type == 'interval':
            # 验证间隔配置
            interval_config = schedule_config.get('interval', {})
            if not interval_config:
                errors.append("interval类型调度缺少interval配置")
            
            # 检查至少有一个时间单位
            time_units = ['seconds', 'minutes', 'hours', 'days', 'weeks']
            if not any(interval_config.get(unit, 0) > 0 for unit in time_units):
                errors.append("interval配置必须指定至少一个时间单位")
        
        elif schedule_type == 'date':
            # 验证日期配置
            run_date = schedule_config.get('date', {}).get('run_date')
            if not run_date:
                errors.append("date类型调度缺少run_date配置")
        
        else:
            errors.append(f"不支持的调度类型: {schedule_type}")
        
        return errors
    
    def _validate_ai_config(self, ai_config: Dict[str, Any]) -> list:
        """
        验证AI配置
        
        Args:
            ai_config: AI配置
            
        Returns:
            验证错误列表
        """
        errors = []
        
        provider = ai_config.get('provider')
        if not provider:
            errors.append("AI配置缺少provider字段")
        elif provider not in ['claude', 'deepseek']:
            errors.append(f"不支持的AI提供商: {provider}")
        
        # 检查API密钥
        api_key = ai_config.get('api_key')
        if not api_key:
            errors.append("AI配置缺少api_key字段")
        
        return errors
    
    def _validate_git_config(self, git_config: Dict[str, Any]) -> list:
        """
        验证Git配置
        
        Args:
            git_config: Git配置
            
        Returns:
            验证错误列表
        """
        errors = []
        
        platform = git_config.get('platform')
        if not platform:
            errors.append("Git配置缺少platform字段")
        elif platform not in ['github', 'gitlab']:
            errors.append(f"不支持的Git平台: {platform}")
        
        # 检查访问令牌
        token = git_config.get('token')
        if not token:
            errors.append("Git配置缺少token字段")
        
        # 检查仓库信息
        repo_url = git_config.get('repo_url')
        if not repo_url:
            errors.append("Git配置缺少repo_url字段")
        
        return errors
