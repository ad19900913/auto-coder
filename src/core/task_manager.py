"""
任务管理器 - 负责任务的调度、执行和状态管理
"""

import logging
import threading
import time
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, Future

from .scheduler import TaskScheduler
from .task_executor_factory import TaskExecutorFactory
from .state_manager import StateManager, TaskStatus
from .config_manager import ConfigManager
from .dependency_manager import DependencyManager
from ..services.notify_service import NotifyService


class TaskManager:
    """任务管理器，负责任务的调度、执行和状态管理"""
    
    def __init__(self, config_manager: ConfigManager, state_manager: StateManager, 
                 notify_service: NotifyService, max_workers: int = 5):
        """
        初始化任务管理器
        
        Args:
            config_manager: 配置管理器
            state_manager: 状态管理器
            notify_service: 通知服务
            max_workers: 最大工作线程数
        """
        self.config_manager = config_manager
        self.state_manager = state_manager
        self.notify_service = notify_service
        self.max_workers = max_workers
        
        self.logger = logging.getLogger(__name__)
        
        # 初始化组件
        self.scheduler = TaskScheduler(config_manager, max_workers)
        self.executor_factory = TaskExecutorFactory(config_manager, state_manager, notify_service)
        self.dependency_manager = DependencyManager()
        
        # 任务执行状态
        self.running_tasks = {}
        self.task_futures = {}
        self.executor_pool = ThreadPoolExecutor(max_workers=max_workers)
        
        # 线程锁
        self._lock = threading.Lock()
        
        # 停止标志
        self._stop_flag = False
        
        self.logger.debug("任务管理器初始化完成")
    
    def start(self):
        """启动任务管理器"""
        try:
            # 启动调度器
            self.scheduler.start()
            
            # 加载并调度所有任务
            self._load_and_schedule_tasks()
            
            self.logger.info("任务管理器启动成功")
            
        except Exception as e:
            self.logger.error(f"启动任务管理器失败: {e}")
            raise
    
    def stop(self):
        """停止任务管理器"""
        try:
            self._stop_flag = True
            
            # 停止调度器
            self.scheduler.stop()
            
            # 等待所有运行中的任务完成
            self._wait_for_running_tasks()
            
            # 关闭线程池
            self.executor_pool.shutdown(wait=True)
            
            self.logger.info("任务管理器已停止")
            
        except Exception as e:
            self.logger.error(f"停止任务管理器失败: {e}")
    
    def _load_and_schedule_tasks(self):
        """加载并调度所有任务"""
        try:
            # 获取所有任务配置
            task_configs = self.config_manager.get_all_task_configs()
            
            # 首先构建依赖图
            self._build_dependency_graph(task_configs)
            
            # 检查循环依赖
            cycles = self.dependency_manager.check_circular_dependencies()
            if cycles:
                self.logger.error(f"发现循环依赖，无法启动: {cycles}")
                return
            
            # 获取执行顺序
            execution_order = self.dependency_manager.get_execution_order()
            if not execution_order:
                self.logger.error("无法确定任务执行顺序")
                return
            
            # 按执行顺序调度任务
            for layer_index, task_layer in enumerate(execution_order):
                for task_id in task_layer:
                    try:
                        task_config = task_configs.get(task_id)
                        if not task_config:
                            continue
                        
                        # 检查任务是否启用
                        if not task_config.get('enabled', True):
                            self.logger.info(f"任务已禁用，跳过: {task_id}")
                            continue
                        
                        # 验证任务配置
                        validation_errors = self.executor_factory.validate_task_config(task_id, task_config)
                        if validation_errors:
                            self.logger.error(f"任务配置验证失败 {task_id}: {validation_errors}")
                            continue
                        
                        # 获取调度配置
                        schedule_config = task_config.get('schedule', {})
                        if not schedule_config:
                            self.logger.warning(f"任务缺少调度配置，跳过: {task_id}")
                            continue
                        
                        # 获取任务优先级
                        priority = task_config.get('priority', 1)
                        
                        # 添加到调度器
                        if self.scheduler.add_task(
                            task_id=task_id,
                            task_func=self._execute_task_wrapper,
                            schedule_config=schedule_config,
                            priority=priority,
                            task_config=task_config
                        ):
                            self.logger.info(f"任务调度成功: {task_id} (层级: {layer_index})")
                        else:
                            self.logger.error(f"任务调度失败: {task_id}")
                    
                    except Exception as e:
                        self.logger.error(f"加载任务配置失败 {task_id}: {e}")
                        continue
            
            self.logger.info(f"任务加载完成，共加载 {len(task_configs)} 个任务，执行层级: {len(execution_order)}")
            
        except Exception as e:
            self.logger.error(f"加载任务配置失败: {e}")
    
    def _build_dependency_graph(self, task_configs: Dict[str, Any]):
        """构建依赖图"""
        try:
            for task_id, task_config in task_configs.items():
                # 获取依赖配置
                dependencies = task_config.get('dependencies', [])
                priority = task_config.get('priority', 1)
                resource_requirements = task_config.get('resource_requirements', {})
                
                # 添加到依赖管理器
                self.dependency_manager.add_task(
                    task_id=task_id,
                    dependencies=dependencies,
                    priority=priority,
                    resource_requirements=resource_requirements
                )
            
            self.logger.info(f"依赖图构建完成，共 {len(task_configs)} 个任务")
            
        except Exception as e:
            self.logger.error(f"构建依赖图失败: {e}")
    
    def _execute_task_wrapper(self, task_id: str, task_config: Dict[str, Any] = None):
        """
        任务执行包装器
        
        Args:
            task_id: 任务ID
            task_config: 任务配置
        """
        try:
            # 检查任务是否应该执行
            if not self._should_execute_task(task_id):
                self.logger.info(f"任务跳过执行: {task_id}")
                return
            
            # 检查依赖是否满足
            if not self.dependency_manager.can_execute_task(task_id):
                self.logger.info(f"任务依赖未满足，跳过执行: {task_id}")
                return
            
            # 分配资源
            task_node = self.dependency_manager.task_graph.get(task_id)
            if task_node and task_node.resource_requirements:
                if not self.dependency_manager.resource_manager.allocate_resources(task_id, task_node.resource_requirements):
                    self.logger.warning(f"资源不足，跳过执行: {task_id}")
                    return
            
            # 标记任务开始执行
            self.dependency_manager._executing_tasks.add(task_id)
            
            # 创建任务执行器
            executor = self.executor_factory.create_executor(task_id)
            
            # 提交任务到线程池
            future = self.executor_pool.submit(self._execute_task_safe, executor)
            
            # 记录任务状态
            with self._lock:
                self.running_tasks[task_id] = executor
                self.task_futures[task_id] = future
            
            # 等待任务完成
            result = future.result()
            
            # 清理任务状态
            with self._lock:
                self.running_tasks.pop(task_id, None)
                self.task_futures.pop(task_id, None)
            
            # 标记任务完成
            if result.get('success', False):
                self.dependency_manager.mark_task_completed(task_id, result)
            else:
                self.dependency_manager.mark_task_failed(task_id, result.get('error'))
            
            self.logger.info(f"任务执行完成: {task_id}, 结果: {result}")
            
        except Exception as e:
            self.logger.error(f"任务执行包装器异常 {task_id}: {e}")
            
            # 清理任务状态
            with self._lock:
                self.running_tasks.pop(task_id, None)
                self.task_futures.pop(task_id, None)
            
            # 标记任务失败
            self.dependency_manager.mark_task_failed(task_id, str(e))
    
    def _execute_task_safe(self, executor) -> Dict[str, Any]:
        """
        安全执行任务
        
        Args:
            executor: 任务执行器
            
        Returns:
            执行结果
        """
        try:
            return executor.execute()
        except Exception as e:
            self.logger.error(f"任务执行异常 {executor.task_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def _should_execute_task(self, task_id: str) -> bool:
        """
        判断任务是否应该执行
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否应该执行
        """
        try:
            # 检查任务状态
            task_status_enum = self.state_manager.get_task_status(task_id)
            if not task_status_enum:
                return True
            
            # 检查任务是否已在运行
            if task_id in self.running_tasks:
                self.logger.warning(f"任务已在运行中: {task_id}")
                return False
            
            # 检查任务状态
            if task_status_enum in [TaskStatus.RUNNING, TaskStatus.REVIEWING]:
                self.logger.warning(f"任务状态不允许执行: {task_id} -> {task_status_enum.value}")
                return False
            
            # 检查重试次数
            max_attempts = self._get_task_max_attempts(task_id)
            state_data = self.state_manager.load_state_file(task_id)
            current_attempts = state_data.get('attempts', 0) if state_data else 0
            
            if current_attempts >= max_attempts:
                self.logger.warning(f"任务重试次数已达上限: {task_id} ({current_attempts}/{max_attempts})")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"判断任务执行条件失败 {task_id}: {e}")
            return False
    
    def _get_task_max_attempts(self, task_id: str) -> int:
        """
        获取任务最大重试次数
        
        Args:
            task_id: 任务ID
            
        Returns:
            最大重试次数
        """
        try:
            task_config = self.config_manager.get_task_config(task_id)
            if not task_config:
                return 3
            
            # 获取任务级重试配置
            task_retry = task_config.get('retry', {})
            max_attempts = task_retry.get('max_attempts')
            
            if max_attempts is not None:
                return max_attempts
            
            # 获取全局重试配置
            global_retry = self.config_manager.get_system_config().get('retry_policy', {})
            return global_retry.get('max_attempts', 3)
            
        except Exception as e:
            self.logger.warning(f"获取任务最大重试次数失败 {task_id}: {e}")
            return 3
    
    def _wait_for_running_tasks(self, timeout: int = 60):
        """
        等待运行中的任务完成
        
        Args:
            timeout: 超时时间（秒）
        """
        try:
            start_time = time.time()
            
            while self.running_tasks and (time.time() - start_time) < timeout:
                # 检查任务状态
                completed_tasks = []
                
                for task_id, future in self.task_futures.items():
                    if future.done():
                        completed_tasks.append(task_id)
                
                # 清理已完成的任务
                for task_id in completed_tasks:
                    with self._lock:
                        self.running_tasks.pop(task_id, None)
                        self.task_futures.pop(task_id, None)
                
                if not self.running_tasks:
                    break
                
                time.sleep(1)
            
            if self.running_tasks:
                self.logger.warning(f"等待任务完成超时，仍有 {len(self.running_tasks)} 个任务在运行")
            
        except Exception as e:
            self.logger.error(f"等待任务完成失败: {e}")
    
    def execute_task_now(self, task_id: str) -> bool:
        """
        立即执行指定任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功提交执行
        """
        try:
            # 检查任务是否存在
            task_config = self.config_manager.get_task_config(task_id)
            if not task_config:
                self.logger.error(f"任务配置不存在: {task_id}")
                return False
            
            # 检查任务是否已在运行
            if task_id in self.running_tasks:
                self.logger.warning(f"任务已在运行中: {task_id}")
                return False
            
            # 创建任务执行器
            executor = self.executor_factory.create_executor(task_id)
            
            # 提交任务到线程池
            future = self.executor_pool.submit(self._execute_task_safe, executor)
            
            # 记录任务状态
            with self._lock:
                self.running_tasks[task_id] = executor
                self.task_futures[task_id] = future
            
            self.logger.info(f"任务已提交立即执行: {task_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"立即执行任务失败 {task_id}: {e}")
            return False
    
    def execute_task_with_workflow(self, task_id: str) -> bool:
        """
        使用工作流引擎执行指定任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功提交执行
        """
        try:
            # 检查任务是否存在
            task_config = self.config_manager.get_task_config(task_id)
            if not task_config:
                self.logger.error(f"任务配置不存在: {task_id}")
                return False
            
            # 检查任务是否已在运行
            if task_id in self.running_tasks:
                self.logger.warning(f"任务已在运行中: {task_id}")
                return False
            
            # 创建任务执行器
            executor = self.executor_factory.create_executor(task_id)
            
            # 提交工作流任务到线程池
            future = self.executor_pool.submit(self._execute_workflow_task_safe, executor)
            
            # 记录任务状态
            with self._lock:
                self.running_tasks[task_id] = executor
                self.task_futures[task_id] = future
            
            self.logger.info(f"工作流任务已提交立即执行: {task_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"立即执行工作流任务失败 {task_id}: {e}")
            return False
    
    def stop_task(self, task_id: str) -> bool:
        """
        停止指定任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功停止
        """
        try:
            with self._lock:
                if task_id not in self.running_tasks:
                    self.logger.warning(f"任务未在运行: {task_id}")
                    return False
                
                # 获取任务执行器和Future
                executor = self.running_tasks[task_id]
                future = self.task_futures.get(task_id)
                
                # 取消Future
                if future and not future.done():
                    future.cancel()
                
                # 清理任务状态
                self.running_tasks.pop(task_id, None)
                self.task_futures.pop(task_id, None)
                
                # 更新任务状态
                self.state_manager.update_task_status(
                    task_id, 
                    TaskStatus.CANCELLED,
                    metadata={'cancelled_at': datetime.now().isoformat()}
                )
            
            self.logger.info(f"任务已停止: {task_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"停止任务失败 {task_id}: {e}")
            return False
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务状态信息
        """
        try:
            # 获取基本状态信息
            status_info = self.state_manager.get_task_status(task_id)
            if not status_info:
                return None
            
            # 检查是否在运行
            is_running = task_id in self.running_tasks
            
            # 获取调度信息
            scheduler_info = self.scheduler.get_task_info(task_id)
            
            # 合并信息
            task_status = {
                'task_id': task_id,
                'is_running': is_running,
                'status': status_info.get('status'),
                'progress': status_info.get('progress', 0),
                'attempts': status_info.get('attempts', 0),
                'errors': status_info.get('errors', 0),
                'last_run_time': status_info.get('last_run_time'),
                'next_run_time': scheduler_info.get('next_run_time') if scheduler_info else None,
                'executor': status_info.get('metadata', {}).get('executor'),
                'metadata': status_info.get('metadata', {})
            }
            
            return task_status
            
        except Exception as e:
            self.logger.error(f"获取任务状态失败 {task_id}: {e}")
            return None
    
    def get_all_task_statuses(self) -> List[Dict[str, Any]]:
        """
        获取所有任务状态
        
        Returns:
            任务状态列表
        """
        try:
            task_statuses = []
            
            # 获取所有任务配置
            task_configs = self.config_manager.get_all_task_configs()
            
            for task_id in task_configs.keys():
                task_status = self.get_task_status(task_id)
                if task_status:
                    task_statuses.append(task_status)
            
            return task_statuses
            
        except Exception as e:
            self.logger.error(f"获取所有任务状态失败: {e}")
            return []
    
    def get_running_tasks(self) -> List[str]:
        """
        获取正在运行的任务ID列表
        
        Returns:
            正在运行的任务ID列表
        """
        with self._lock:
            return list(self.running_tasks.keys())
    
    def get_scheduler_stats(self) -> Dict[str, Any]:
        """
        获取调度器统计信息
        
        Returns:
            调度器统计信息
        """
        return self.scheduler.get_stats()
    
    def is_running(self) -> bool:
        """检查任务管理器是否正在运行"""
        return not self._stop_flag and self.scheduler.is_running()
    
    # 依赖管理相关方法
    def get_dependency_graph(self) -> Dict[str, Any]:
        """
        获取依赖图信息
        
        Returns:
            依赖图信息
        """
        return self.dependency_manager.get_dependency_graph()
    
    def get_task_dependencies(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务依赖信息
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务依赖信息
        """
        return self.dependency_manager.get_task_status(task_id)
    
    def get_ready_tasks(self) -> List[str]:
        """
        获取可以执行的任务列表
        
        Returns:
            可执行任务列表
        """
        return self.dependency_manager.get_ready_tasks()
    
    def get_resource_status(self) -> Dict[str, Any]:
        """
        获取资源状态
        
        Returns:
            资源状态信息
        """
        return self.dependency_manager.resource_manager.get_resource_status()
    
    def add_task_dependency(self, task_id: str, dependency_task_id: str, 
                           dependency_type: str = "required", condition: Callable = None) -> bool:
        """
        添加任务依赖
        
        Args:
            task_id: 任务ID
            dependency_task_id: 依赖任务ID
            dependency_type: 依赖类型
            condition: 条件函数
            
        Returns:
            是否添加成功
        """
        try:
            # 检查任务是否存在
            if task_id not in self.dependency_manager.task_graph:
                self.logger.error(f"任务不存在: {task_id}")
                return False
            
            if dependency_task_id not in self.dependency_manager.task_graph:
                self.logger.error(f"依赖任务不存在: {dependency_task_id}")
                return False
            
            # 创建依赖信息
            dependency_info = {
                'task_id': dependency_task_id,
                'type': dependency_type,
                'condition': condition
            }
            
            # 添加到依赖图
            task_node = self.dependency_manager.task_graph[task_id]
            dep_info = self.dependency_manager.DependencyInfo(
                task_id=dependency_task_id,
                dependency_type=self.dependency_manager.DependencyType(dependency_type),
                condition=condition
            )
            task_node.dependencies.append(dep_info)
            
            # 更新依赖关系
            self.dependency_manager._update_dependency_relationships()
            
            self.logger.info(f"依赖添加成功: {task_id} -> {dependency_task_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"添加任务依赖失败: {e}")
            return False
    
    def remove_task_dependency(self, task_id: str, dependency_task_id: str) -> bool:
        """
        移除任务依赖
        
        Args:
            task_id: 任务ID
            dependency_task_id: 依赖任务ID
            
        Returns:
            是否移除成功
        """
        try:
            if task_id not in self.dependency_manager.task_graph:
                return False
            
            task_node = self.dependency_manager.task_graph[task_id]
            
            # 移除依赖
            task_node.dependencies = [
                dep for dep in task_node.dependencies 
                if dep.task_id != dependency_task_id
            ]
            
            # 更新依赖关系
            self.dependency_manager._update_dependency_relationships()
            
            self.logger.info(f"依赖移除成功: {task_id} -> {dependency_task_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"移除任务依赖失败: {e}")
            return False
    
    def check_circular_dependencies(self) -> List[List[str]]:
        """
        检查循环依赖
        
        Returns:
            循环依赖列表
        """
        return self.dependency_manager.check_circular_dependencies()
    
    def get_execution_order(self) -> List[List[str]]:
        """
        获取任务执行顺序
        
        Returns:
            执行顺序（分层）
        """
        return self.dependency_manager.get_execution_order()
    
    def _execute_workflow_task_safe(self, executor):
        """
        安全执行工作流任务
        
        Args:
            executor: 任务执行器
        """
        try:
            # 导入asyncio
            import asyncio
            
            # 创建新的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # 执行工作流任务
                result = loop.run_until_complete(executor.execute_with_workflow())
                self.logger.info(f"工作流任务执行完成: {executor.task_id}")
                return result
            finally:
                # 关闭事件循环
                loop.close()
                
        except Exception as e:
            self.logger.error(f"工作流任务执行失败 {executor.task_id}: {e}")
            raise
