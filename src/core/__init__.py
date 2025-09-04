"""
自动化AI任务执行系统 - 核心模块
"""

__version__ = "1.0.0"
__author__ = "Auto Coder Team"
__description__ = "自动化AI任务执行系统核心模块"

# 导入核心类
from .config_manager import ConfigManager
from .config_validator import ConfigValidator
from .state_manager import StateManager, TaskStatus
from .state_file_manager import StateFileManager
from .scheduler import TaskScheduler
from .task_executor import TaskExecutor
from .task_executor_factory import TaskExecutorFactory
from .task_manager import TaskManager
from .dependency_manager import DependencyManager, DependencyType, ResourceManager
from .workflow_engine import WorkflowEngine, WorkflowMode, StepStatus, StepResult, WorkflowContext, WorkflowTemplate

# 导入异常类
from .exceptions import (
    AutoCoderError, ConfigError, TaskError, WorkflowError,
    AIServiceError, GitServiceError, NotificationError,
    StateError, ValidationError, TimeoutError, RetryError
)

__all__ = [
    'ConfigManager',
    'ConfigValidator',
    'StateManager',
    'TaskStatus', 
    'StateFileManager',
    'TaskScheduler',
    'TaskExecutor',
    'TaskExecutorFactory',
    'TaskManager',
    'DependencyManager',
    'DependencyType',
    'ResourceManager',
    'WorkflowEngine',
    'WorkflowMode',
    'StepStatus',
    'StepResult',
    'WorkflowContext',
    'WorkflowTemplate',
    'AutoCoderError',
    'ConfigError',
    'TaskError',
    'WorkflowError',
    'AIServiceError',
    'GitServiceError',
    'NotificationError',
    'StateError',
    'ValidationError',
    'TimeoutError',
    'RetryError'
]
