"""
任务加载器模块
负责任务配置的加载、验证和调度
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from .config_manager import ConfigManager
from .dependency_manager import DependencyManager
from .task_executor_factory import TaskExecutorFactory
from .scheduler import TaskScheduler


class TaskLoader:
    """任务加载器"""
    
    def __init__(self, config_manager: ConfigManager, 
                 dependency_manager: DependencyManager,
                 executor_factory: TaskExecutorFactory,
                 scheduler: TaskScheduler):
        """
        初始化任务加载器
        
        Args:
            config_manager: 配置管理器
            dependency_manager: 依赖管理器
            executor_factory: 任务执行器工厂
            scheduler: 任务调度器
        """
        self.config_manager = config_manager
        self.dependency_manager = dependency_manager
        self.executor_factory = executor_factory
        self.scheduler = scheduler
        self.logger = logging.getLogger(__name__)
    
    def load_and_schedule_tasks(self) -> None:
        """
        加载并调度所有任务
        """
        try:
            # 加载任务配置
            task_configs = self._load_task_configurations()
            if not task_configs:
                self.logger.warning("未找到任何任务配置")
                return
            
            # 构建依赖图
            self._build_dependency_graph(task_configs)
            
            # 检查循环依赖
            if not self._validate_dependencies():
                return
            
            # 获取执行顺序
            execution_order = self._get_execution_order()
            if not execution_order:
                return
            
            # 调度任务
            self._schedule_tasks(task_configs, execution_order)
            
            self.logger.info(f"任务加载完成，共加载 {len(task_configs)} 个任务，执行层级: {len(execution_order)}")
            
        except Exception as e:
            self.logger.error(f"加载任务配置失败: {e}")
    
    def _load_task_configurations(self) -> Dict[str, Any]:
        """
        加载任务配置
        
        Returns:
            任务配置字典
        """
        task_configs = {}
        
        try:
            # 从配置管理器获取任务配置
            all_configs = self.config_manager.get_all_task_configs()
            
            for task_id, task_config in all_configs.items():
                if self._is_valid_task_config(task_id, task_config):
                    task_configs[task_id] = task_config
                else:
                    self.logger.warning(f"跳过无效任务配置: {task_id}")
            
            return task_configs
            
        except Exception as e:
            self.logger.error(f"加载任务配置失败: {e}")
            return {}
    
    def _is_valid_task_config(self, task_id: str, task_config: Dict[str, Any]) -> bool:
        """
        验证任务配置是否有效
        
        Args:
            task_id: 任务ID
            task_config: 任务配置
            
        Returns:
            是否有效
        """
        # 检查基本字段
        if not task_id or not isinstance(task_config, dict):
            return False
        
        # 检查任务类型
        task_type = task_config.get('type')
        if not task_type:
            self.logger.warning(f"任务 {task_id} 缺少类型")
            return False
        
        # 检查调度配置
        schedule_config = task_config.get('schedule')
        if not schedule_config:
            self.logger.warning(f"任务 {task_id} 缺少调度配置")
            return False
        
        return True
    
    def _build_dependency_graph(self, task_configs: Dict[str, Any]) -> None:
        """
        构建依赖图
        
        Args:
            task_configs: 任务配置字典
        """
        try:
            for task_id, task_config in task_configs.items():
                dependencies = task_config.get('dependencies', [])
                priority = task_config.get('priority', 1)
                resource_requirements = task_config.get('resource_requirements', {})
                
                self.dependency_manager.add_task(
                    task_id=task_id,
                    dependencies=dependencies,
                    priority=priority,
                    resource_requirements=resource_requirements
                )
            
            self.logger.info(f"依赖图构建完成，共 {len(task_configs)} 个任务")
            
        except Exception as e:
            self.logger.error(f"构建依赖图失败: {e}")
    
    def _validate_dependencies(self) -> bool:
        """
        验证依赖关系
        
        Returns:
            是否有效
        """
        cycles = self.dependency_manager.check_circular_dependencies()
        if cycles:
            self.logger.error(f"发现循环依赖，无法启动: {cycles}")
            return False
        
        return True
    
    def _get_execution_order(self) -> Optional[List[List[str]]]:
        """
        获取任务执行顺序
        
        Returns:
            执行顺序列表
        """
        execution_order = self.dependency_manager.get_execution_order()
        if not execution_order:
            self.logger.error("无法确定任务执行顺序")
            return None
        
        return execution_order
    
    def _schedule_tasks(self, task_configs: Dict[str, Any], 
                       execution_order: List[List[str]]) -> None:
        """
        调度任务
        
        Args:
            task_configs: 任务配置字典
            execution_order: 执行顺序
        """
        scheduled_count = 0
        
        for layer_index, task_layer in enumerate(execution_order):
            for task_id in task_layer:
                if self._schedule_single_task(task_id, task_configs.get(task_id), layer_index):
                    scheduled_count += 1
        
        self.logger.info(f"成功调度 {scheduled_count} 个任务")
    
    def _schedule_single_task(self, task_id: str, task_config: Dict[str, Any], 
                             layer_index: int) -> bool:
        """
        调度单个任务
        
        Args:
            task_id: 任务ID
            task_config: 任务配置
            layer_index: 层级索引
            
        Returns:
            是否调度成功
        """
        try:
            # 检查任务是否启用
            if not task_config.get('enabled', True):
                self.logger.info(f"任务已禁用，跳过: {task_id}")
                return False
            
            # 验证任务配置
            validation_errors = self.executor_factory.validate_task_config(task_id, task_config)
            if validation_errors:
                self.logger.error(f"任务配置验证失败 {task_id}: {validation_errors}")
                return False
            
            # 获取调度配置
            schedule_config = task_config.get('schedule', {})
            priority = task_config.get('priority', 1)
            
            # 添加到调度器
            success = self.scheduler.add_task(
                task_id=task_id,
                task_func=self._create_task_wrapper(task_id),
                schedule_config=schedule_config,
                priority=priority,
                task_config=task_config
            )
            
            if success:
                self.logger.info(f"任务调度成功: {task_id} (层级: {layer_index})")
                return True
            else:
                self.logger.error(f"任务调度失败: {task_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"调度任务失败 {task_id}: {e}")
            return False
    
    def _create_task_wrapper(self, task_id: str):
        """
        创建任务包装器
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务包装器函数
        """
        def task_wrapper():
            # 这里应该调用任务管理器的执行方法
            # 为了避免循环导入，这里返回一个占位符
            self.logger.info(f"执行任务: {task_id}")
            return True
        
        return task_wrapper
