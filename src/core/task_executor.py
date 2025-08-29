"""
任务执行器基类 - 定义任务执行的标准接口和通用逻辑
"""

import logging
import time
import traceback
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

from .state_manager import StateManager, TaskStatus
from .config_manager import ConfigManager
from ..services.notify_service import NotifyService
from ..services.ai_service import AIService
from ..services.git_service import GitService


class TaskExecutor(ABC):
    """任务执行器抽象基类"""
    
    def __init__(self, task_id: str, config_manager: ConfigManager, 
                 state_manager: StateManager, notify_service: NotifyService):
        """
        初始化任务执行器
        
        Args:
            task_id: 任务ID
            config_manager: 配置管理器
            state_manager: 状态管理器
            notify_service: 通知服务
        """
        self.task_id = task_id
        self.config_manager = config_manager
        self.state_manager = state_manager
        self.notify_service = notify_service
        
        # 获取任务配置
        self.task_config = self.config_manager.get_task_config(task_id)
        if not self.task_config:
            raise ValueError(f"任务配置不存在: {task_id}")
        
        # 初始化日志记录器
        self.logger = logging.getLogger(f"{__name__}.{task_id}")
        
        # 初始化服务实例
        self.ai_service = None
        self.git_service = None
        
        # 任务执行状态
        self.start_time = None
        self.end_time = None
        self.execution_result = {}
        
        # 初始化服务
        self._init_services()
    
    def _init_services(self):
        """初始化AI和Git服务"""
        try:
            # 初始化AI服务
            ai_config = self.task_config.get('ai', {})
            ai_provider = ai_config.get('provider', 'claude')
            
            if ai_provider == 'claude':
                from ..services.ai_service import ClaudeService
                self.ai_service = ClaudeService(self.config_manager)
            elif ai_provider == 'deepseek':
                from ..services.ai_service import DeepSeekService
                self.ai_service = DeepSeekService(self.config_manager)
            else:
                raise ValueError(f"不支持的AI服务提供商: {ai_provider}")
            
            # 初始化Git服务
            git_config = self.task_config.get('git', {})
            git_platform = git_config.get('platform', 'github')
            
            if git_platform == 'github':
                from ..services.git_service import GitHubService
                self.git_service = GitHubService(self.config_manager)
            elif git_platform == 'gitlab':
                from ..services.git_service import GitLabService
                self.git_service = GitLabService(self.config_manager)
            else:
                raise ValueError(f"不支持的Git平台: {git_platform}")
            
            self.logger.info(f"服务初始化成功: AI={ai_provider}, Git={git_platform}")
            
        except Exception as e:
            self.logger.error(f"服务初始化失败: {e}")
            raise
    
    def execute(self) -> Dict[str, Any]:
        """
        执行任务的主方法
        
        Returns:
            执行结果字典
        """
        try:
            # 开始执行
            self._pre_execute()
            
            # 执行具体任务
            result = self._execute_task()
            
            # 执行后处理
            self._post_execute(result)
            
            return result
            
        except Exception as e:
            # 异常处理
            self._handle_execution_error(e)
            raise
    
    def _pre_execute(self):
        """任务执行前的准备工作"""
        try:
            self.start_time = datetime.now()
            
            # 更新任务状态为运行中
            self.state_manager.update_task_status(
                self.task_id, 
                TaskStatus.RUNNING,
                progress=0,
                metadata={
                    'start_time': self.start_time.isoformat(),
                    'executor': self.__class__.__name__
                }
            )
            
            # 发送任务开始通知
            self.notify_service.notify_task_start(
                task_id=self.task_id,
                task_type=self.task_config.get('type', 'unknown'),
                start_time=self.start_time
            )
            
            self.logger.info(f"任务开始执行: {self.task_id}")
            
        except Exception as e:
            self.logger.error(f"任务执行前准备失败: {e}")
            raise
    
    @abstractmethod
    def _execute_task(self) -> Dict[str, Any]:
        """
        执行具体任务的抽象方法
        
        Returns:
            任务执行结果
        """
        pass
    
    def _post_execute(self, result: Dict[str, Any]):
        """任务执行后的处理工作"""
        try:
            self.end_time = datetime.now()
            execution_time = (self.end_time - self.start_time).total_seconds()
            
            # 更新执行结果
            self.execution_result = result
            self.execution_result.update({
                'execution_time': execution_time,
                'start_time': self.start_time.isoformat(),
                'end_time': self.end_time.isoformat()
            })
            
            # 更新任务状态
            if result.get('success', False):
                status = TaskStatus.COMPLETED
                progress = 100
            else:
                status = TaskStatus.FAILED
                progress = 0
            
            self.state_manager.update_task_status(
                self.task_id,
                status,
                progress=progress,
                metadata=self.execution_result
            )
            
            # 发送任务完成通知
            if status == TaskStatus.COMPLETED:
                self.notify_service.notify_task_complete(
                    task_id=self.task_id,
                    task_type=self.task_config.get('type', 'unknown'),
                    execution_time=execution_time,
                    result=result
                )
            else:
                self.notify_service.notify_task_error(
                    task_id=self.task_id,
                    task_type=self.task_config.get('type', 'unknown'),
                    error_message=result.get('error', '未知错误'),
                    execution_time=execution_time
                )
            
            self.logger.info(f"任务执行完成: {self.task_id}, 耗时: {execution_time:.2f}秒")
            
        except Exception as e:
            self.logger.error(f"任务执行后处理失败: {e}")
            raise
    
    def _handle_execution_error(self, error: Exception):
        """处理任务执行异常"""
        try:
            self.end_time = datetime.now()
            execution_time = (self.end_time - self.start_time).total_seconds() if self.start_time else 0
            
            error_info = {
                'error_type': type(error).__name__,
                'error_message': str(error),
                'traceback': traceback.format_exc(),
                'execution_time': execution_time
            }
            
            # 更新任务状态为失败
            self.state_manager.update_task_status(
                self.task_id,
                TaskStatus.FAILED,
                progress=0,
                metadata=error_info
            )
            
            # 增加错误计数
            self.state_manager.increment_task_errors(self.task_id)
            
            # 发送错误通知
            self.notify_service.notify_task_error(
                task_id=self.task_id,
                task_type=self.task_config.get('type', 'unknown'),
                error_message=str(error),
                execution_time=execution_time,
                error_details=error_info
            )
            
            self.logger.error(f"任务执行异常: {self.task_id}, 错误: {error}")
            
        except Exception as e:
            self.logger.error(f"处理执行异常失败: {e}")
    
    def _update_progress(self, progress: int, message: str = ""):
        """
        更新任务执行进度
        
        Args:
            progress: 进度百分比 (0-100)
            message: 进度描述信息
        """
        try:
            self.state_manager.update_task_progress(
                self.task_id,
                progress,
                message
            )
            
            if message:
                self.logger.info(f"任务进度更新: {progress}% - {message}")
            else:
                self.logger.debug(f"任务进度更新: {progress}%")
                
        except Exception as e:
            self.logger.warning(f"更新任务进度失败: {e}")
    
    def _add_metadata(self, key: str, value: Any):
        """
        添加任务元数据
        
        Args:
            key: 元数据键
            value: 元数据值
        """
        try:
            self.state_manager.add_task_metadata(
                self.task_id,
                key,
                value
            )
        except Exception as e:
            self.logger.warning(f"添加任务元数据失败: {e}")
    
    def _get_output_path(self, output_type: str, filename: str = None) -> Path:
        """
        获取输出文件路径
        
        Args:
            output_type: 输出类型 (reviews, docs, requirement_reviews, custom_tasks)
            filename: 文件名，如果为None则自动生成
            
        Returns:
            输出文件路径
        """
        try:
            # 获取输出目录配置
            output_config = self.config_manager.get_system_config().get('outputs', {})
            base_dir = output_config.get('base_directory', 'outputs')
            
            # 构建输出目录
            output_dir = Path(base_dir) / output_type
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成文件名
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{self.task_id}_{timestamp}.md"
            
            return output_dir / filename
            
        except Exception as e:
            self.logger.error(f"获取输出路径失败: {e}")
            # 返回默认路径
            return Path(f"outputs/{output_type}/{self.task_id}.md")
    
    def _save_output(self, content: str, output_type: str, filename: str = None) -> str:
        """
        保存输出内容到文件
        
        Args:
            content: 输出内容
            output_type: 输出类型
            filename: 文件名
            
        Returns:
            保存的文件路径
        """
        try:
            output_path = self._get_output_path(output_type, filename)
            
            # 确保目录存在
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"输出文件保存成功: {output_path}")
            
            # 添加到元数据
            self._add_metadata('output_file', str(output_path))
            
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"保存输出文件失败: {e}")
            raise
    
    def _get_retry_config(self) -> Dict[str, Any]:
        """
        获取重试配置
        
        Returns:
            重试配置字典
        """
        try:
            # 获取任务级重试配置
            task_retry = self.task_config.get('retry', {})
            
            # 获取全局重试配置
            global_retry = self.config_manager.get_system_config().get('retry_policy', {})
            
            # 合并配置，任务级配置优先
            retry_config = global_retry.copy()
            retry_config.update(task_retry)
            
            return retry_config
            
        except Exception as e:
            self.logger.warning(f"获取重试配置失败: {e}")
            # 返回默认配置
            return {
                'max_attempts': 3,
                'base_delay': 5,
                'max_delay': 300,
                'backoff_multiplier': 2,
                'jitter': 0.1
            }
    
    def _should_retry(self, attempt: int, error: Exception) -> bool:
        """
        判断是否应该重试
        
        Args:
            attempt: 当前尝试次数
            error: 执行异常
            
        Returns:
            是否应该重试
        """
        try:
            retry_config = self._get_retry_config()
            max_attempts = retry_config.get('max_attempts', 3)
            
            # 检查尝试次数
            if attempt >= max_attempts:
                return False
            
            # 检查错误类型（某些错误不应该重试）
            non_retryable_errors = [
                'ValueError', 'TypeError', 'AttributeError',
                'FileNotFoundError', 'PermissionError'
            ]
            
            error_type = type(error).__name__
            if error_type in non_retryable_errors:
                return False
            
            return True
            
        except Exception as e:
            self.logger.warning(f"判断重试条件失败: {e}")
            return False
    
    def _calculate_retry_delay(self, attempt: int) -> float:
        """
        计算重试延迟时间
        
        Args:
            attempt: 当前尝试次数
            
        Returns:
            延迟时间（秒）
        """
        try:
            retry_config = self._get_retry_config()
            
            base_delay = retry_config.get('base_delay', 5)
            max_delay = retry_config.get('max_delay', 300)
            backoff_multiplier = retry_config.get('backoff_multiplier', 2)
            jitter = retry_config.get('jitter', 0.1)
            
            # 计算指数退避延迟
            delay = min(base_delay * (backoff_multiplier ** (attempt - 1)), max_delay)
            
            # 添加随机抖动
            if jitter > 0:
                import random
                jitter_amount = delay * jitter
                delay += random.uniform(-jitter_amount, jitter_amount)
                delay = max(0, delay)
            
            return delay
            
        except Exception as e:
            self.logger.warning(f"计算重试延迟失败: {e}")
            return 5.0  # 默认5秒
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """
        获取任务执行摘要
        
        Returns:
            执行摘要字典
        """
        return {
            'task_id': self.task_id,
            'task_type': self.task_config.get('type', 'unknown'),
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'execution_time': self.execution_result.get('execution_time', 0),
            'success': self.execution_result.get('success', False),
            'result': self.execution_result
        }
