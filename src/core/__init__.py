"""
自动化AI任务执行系统 - 核心模块
"""

__version__ = "1.0.0"
__author__ = "Auto Coder Team"
__description__ = "自动化AI任务执行系统核心模块"

# 导入核心类
from .config_manager import ConfigManager
from .state_manager import StateManager, TaskStatus
from .state_file_manager import StateFileManager
from .scheduler import TaskScheduler
from .task_executor import TaskExecutor
from .task_executor_factory import TaskExecutorFactory
from .task_manager import TaskManager

__all__ = [
    'ConfigManager',
    'StateManager',
    'TaskStatus', 
    'StateFileManager',
    'TaskScheduler',
    'TaskExecutor',
    'TaskExecutorFactory',
    'TaskManager'
]
