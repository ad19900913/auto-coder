"""
任务执行器 - 实现任务执行逻辑、超时处理和重试机制
"""

import time
import logging
import signal
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError


class TaskExecutor:
    """任务执行器，负责执行具体的任务逻辑"""
    
    def __init__(self, config_manager, state_manager, notify_service):
        """
        初始化任务执行器
        
        Args:
            config_manager: 配置管理器实例
            state_manager: 状态管理器实例
            notify_service: 通知服务实例
        """
        self.config_manager = config_manager
        self.state_manager = state_manager
        self.notify_service = notify_service
        self.logger = logging.getLogger(__name__)
        
        # 线程池执行器
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        # 任务执行状态
        self.running_tasks = {}
        
        self.logger.info("任务执行器初始化完成")
    
    def execute_task(self, task_id: str, task_config: Dict[str, Any]) -> bool:
        """
        执行任务
        
        Args:
            task_id: 任务ID
            task_config: 任务配置
            
        Returns:
            执行是否成功
        """
        try:
            # 检查任务是否已经在运行
            if task_id in self.running_tasks:
                self.logger.warning(f"任务已在运行中: {task_id}")
                return False
            
            # 创建任务状态
            self.state_manager.create_state_file(task_id, task_config.get('type', 'unknown'))
            
            # 更新状态为运行中
            self.state_manager.update_status(
                task_id, 
                self.state_manager.TaskStatus.RUNNING,
                "任务开始执行"
            )
            
            # 发送任务开始通知
            self.notify_service.notify_task_start(task_config)
            
            # 记录开始时间
            start_time = time.time()
            self.running_tasks[task_id] = {
                'start_time': start_time,
                'config': task_config,
                'status': 'running'
            }
            
            # 获取任务超时时间
            timeout = self.config_manager.get_task_timeout(task_config.get('type', 'unknown'))
            
            # 执行任务逻辑
            success = self._execute_task_logic(task_id, task_config, timeout)
            
            # 计算执行时间
            duration = time.time() - start_time
            
            # 更新任务状态
            if success:
                self.state_manager.update_status(
                    task_id,
                    self.state_manager.TaskStatus.COMPLETED,
                    "任务执行完成"
                )
                
                # 发送任务完成通知
                self.notify_service.notify_task_complete(task_config, duration)
                
                self.logger.info(f"任务执行成功: {task_id}, 耗时: {duration:.2f}秒")
            else:
                self.state_manager.update_status(
                    task_id,
                    self.state_manager.TaskStatus.FAILED,
                    "任务执行失败"
                )
                
                # 发送任务失败通知
                self.notify_service.notify_task_error(task_config, "任务执行失败")
                
                self.logger.error(f"任务执行失败: {task_id}")
            
            # 清理运行状态
            self.running_tasks.pop(task_id, None)
            
            return success
            
        except Exception as e:
            self.logger.error(f"任务执行异常 {task_id}: {e}")
            
            # 更新状态为失败
            self.state_manager.update_status(
                task_id,
                self.state_manager.TaskStatus.FAILED,
                f"任务执行异常: {str(e)}"
            )
            
            # 发送任务失败通知
            self.notify_service.notify_task_error(task_config, str(e))
            
            # 清理运行状态
            self.running_tasks.pop(task_id, None)
            
            return False
    
    def _execute_task_logic(self, task_id: str, task_config: Dict[str, Any], 
                           timeout: int) -> bool:
        """
        执行任务逻辑
        
        Args:
            task_id: 任务ID
            task_config: 任务配置
            timeout: 超时时间（秒）
            
        Returns:
            执行是否成功
        """
        try:
            # 获取任务类型
            task_type = task_config.get('type', 'unknown')
            
            # 根据任务类型执行相应的逻辑
            if task_type == 'coding':
                return self._execute_coding_task(task_id, task_config, timeout)
            elif task_type == 'review':
                return self._execute_review_task(task_id, task_config, timeout)
            elif task_type == 'doc':
                return self._execute_doc_task(task_id, task_config, timeout)
            elif task_type == 'requirement_review':
                return self._execute_requirement_review_task(task_id, task_config, timeout)
            elif task_type == 'custom':
                return self._execute_custom_task(task_id, task_config, timeout)
            else:
                self.logger.error(f"不支持的任务类型: {task_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"执行任务逻辑失败 {task_id}: {e}")
            return False
    
    def _execute_coding_task(self, task_id: str, task_config: Dict[str, Any], 
                            timeout: int) -> bool:
        """
        执行编码任务
        
        Args:
            task_id: 任务ID
            task_config: 任务配置
            timeout: 超时时间
            
        Returns:
            执行是否成功
        """
        try:
            self.logger.info(f"开始执行编码任务: {task_id}")
            
            # 更新进度
            self.state_manager.set_progress(task_id, 0.1, "开始编码任务")
            
            # 这里应该调用实际的编码逻辑
            # 目前只是模拟执行
            time.sleep(2)
            
            # 更新进度
            self.state_manager.set_progress(task_id, 0.5, "编码进行中")
            
            # 模拟编码过程
            time.sleep(2)
            
            # 更新进度
            self.state_manager.set_progress(task_id, 1.0, "编码完成")
            
            self.logger.info(f"编码任务执行完成: {task_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"编码任务执行失败 {task_id}: {e}")
            return False
    
    def _execute_review_task(self, task_id: str, task_config: Dict[str, Any], 
                            timeout: int) -> bool:
        """
        执行代码审查任务
        
        Args:
            task_id: 任务ID
            task_config: 任务配置
            timeout: 超时时间
            
        Returns:
            执行是否成功
        """
        try:
            self.logger.info(f"开始执行代码审查任务: {task_id}")
            
            # 更新进度
            self.state_manager.set_progress(task_id, 0.1, "开始代码审查")
            
            # 模拟审查过程
            time.sleep(1)
            
            # 更新进度
            self.state_manager.set_progress(task_id, 0.5, "审查进行中")
            
            time.sleep(1)
            
            # 更新进度
            self.state_manager.set_progress(task_id, 1.0, "审查完成")
            
            self.logger.info(f"代码审查任务执行完成: {task_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"代码审查任务执行失败 {task_id}: {e}")
            return False
    
    def _execute_doc_task(self, task_id: str, task_config: Dict[str, Any], 
                         timeout: int) -> bool:
        """
        执行文档生成任务
        
        Args:
            task_id: 任务ID
            task_config: 任务配置
            timeout: 超时时间
            
        Returns:
            执行是否成功
        """
        try:
            self.logger.info(f"开始执行文档生成任务: {task_id}")
            
            # 更新进度
            self.state_manager.set_progress(task_id, 0.1, "开始生成文档")
            
            # 模拟文档生成过程
            time.sleep(1)
            
            # 更新进度
            self.state_manager.set_progress(task_id, 0.5, "文档生成中")
            
            time.sleep(1)
            
            # 更新进度
            self.state_manager.set_progress(task_id, 1.0, "文档生成完成")
            
            self.logger.info(f"文档生成任务执行完成: {task_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"文档生成任务执行失败 {task_id}: {e}")
            return False
    
    def _execute_requirement_review_task(self, task_id: str, task_config: Dict[str, Any], 
                                       timeout: int) -> bool:
        """
        执行需求评审任务
        
        Args:
            task_id: 任务ID
            task_config: 任务配置
            timeout: 超时时间
            
        Returns:
            执行是否成功
        """
        try:
            self.logger.info(f"开始执行需求评审任务: {task_id}")
            
            # 更新进度
            self.state_manager.set_progress(task_id, 0.1, "开始需求评审")
            
            # 模拟评审过程
            time.sleep(2)
            
            # 更新进度
            self.state_manager.set_progress(task_id, 0.5, "评审进行中")
            
            time.sleep(2)
            
            # 更新进度
            self.state_manager.set_progress(task_id, 1.0, "评审完成")
            
            self.logger.info(f"需求评审任务执行完成: {task_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"需求评审任务执行失败 {task_id}: {e}")
            return False
    
    def _execute_custom_task(self, task_id: str, task_config: Dict[str, Any], 
                           timeout: int) -> bool:
        """
        执行自定义任务
        
        Args:
            task_id: 任务ID
            task_config: 任务配置
            timeout: 超时时间
            
        Returns:
            执行是否成功
        """
        try:
            self.logger.info(f"开始执行自定义任务: {task_id}")
            
            # 更新进度
            self.state_manager.set_progress(task_id, 0.1, "开始执行自定义任务")
            
            # 模拟自定义任务执行
            time.sleep(1)
            
            # 更新进度
            self.state_manager.set_progress(task_id, 0.5, "自定义任务执行中")
            
            time.sleep(1)
            
            # 更新进度
            self.state_manager.set_progress(task_id, 1.0, "自定义任务执行完成")
            
            self.logger.info(f"自定义任务执行完成: {task_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"自定义任务执行失败 {task_id}: {e}")
            return False
    
    def cancel_task(self, task_id: str) -> bool:
        """
        取消任务执行
        
        Args:
            task_id: 任务ID
            
        Returns:
            取消是否成功
        """
        try:
            if task_id not in self.running_tasks:
                self.logger.warning(f"任务不在运行中: {task_id}")
                return False
            
            # 更新状态为已取消
            self.state_manager.update_status(
                task_id,
                self.state_manager.TaskStatus.CANCELLED,
                "任务被取消"
            )
            
            # 清理运行状态
            self.running_tasks.pop(task_id, None)
            
            self.logger.info(f"任务取消成功: {task_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"取消任务失败 {task_id}: {e}")
            return False
    
    def get_running_tasks(self) -> Dict[str, Dict[str, Any]]:
        """
        获取正在运行的任务
        
        Returns:
            运行中任务信息字典
        """
        return self.running_tasks.copy()
    
    def get_task_progress(self, task_id: str) -> Optional[float]:
        """
        获取任务进度
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务进度（0.0-1.0），如果任务不存在则返回None
        """
        state_data = self.state_manager.load_state_file(task_id)
        if state_data:
            return state_data.get('progress', 0.0)
        return None
    
    def shutdown(self):
        """关闭任务执行器"""
        try:
            # 取消所有运行中的任务
            for task_id in list(self.running_tasks.keys()):
                self.cancel_task(task_id)
            
            # 关闭线程池
            self.executor.shutdown(wait=True)
            
            self.logger.info("任务执行器已关闭")
            
        except Exception as e:
            self.logger.error(f"关闭任务执行器失败: {e}")
    
    @contextmanager
    def timeout_context(self, timeout_seconds: int):
        """
        超时上下文管理器
        
        Args:
            timeout_seconds: 超时时间（秒）
        """
        def timeout_handler(signum, frame):
            raise TimeoutError(f"任务执行超时: {timeout_seconds}秒")
        
        # 设置信号处理器
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout_seconds)
        
        try:
            yield
        finally:
            # 恢复信号处理器
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
    
    def _handle_timeout(self, task_id: str, task_config: Dict[str, Any]):
        """
        处理任务超时
        
        Args:
            task_id: 任务ID
            task_config: 任务配置
        """
        self.logger.warning(f"任务执行超时: {task_id}")
        
        # 更新状态
        self.state_manager.update_status(
            task_id,
            self.state_manager.TaskStatus.FAILED,
            "任务执行超时"
        )
        
        # 发送超时通知
        self.notify_service.notify_task_error(task_config, "任务执行超时")
    
    def _should_retry(self, task_id: str, error: Exception) -> bool:
        """
        判断是否应该重试
        
        Args:
            task_id: 任务ID
            error: 错误信息
            
        Returns:
            是否应该重试
        """
        # 检查任务是否可以重试
        if not self.state_manager.can_retry(task_id):
            return False
        
        # 检查错误类型是否适合重试
        retryable_errors = (TimeoutError, ConnectionError, OSError)
        return isinstance(error, retryable_errors)
    
    def _schedule_retry(self, task_id: str, task_config: Dict[str, Any], 
                       error: Exception, delay: int):
        """
        安排重试
        
        Args:
            task_id: 任务ID
            task_config: 任务配置
            error: 错误信息
            delay: 延迟时间（秒）
        """
        self.logger.info(f"安排任务重试: {task_id}, 延迟: {delay}秒")
        
        # 这里可以使用调度器安排延迟重试
        # 目前只是记录日志
        pass

