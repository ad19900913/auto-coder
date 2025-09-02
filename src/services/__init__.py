"""
自动化AI任务执行系统 - 服务模块
"""

__version__ = "1.0.0"
__author__ = "Auto Coder Team"
__description__ = "自动化AI任务执行系统服务模块"

# 导入所有服务类
from .notify_service import NotifyService, DingTalkNotifier
from .ai_service import AIService, ClaudeService, DeepSeekService
from .git_service import GitService, GitHubService, GitLabService
from .service_factory import ServiceFactory

__all__ = [
    'NotifyService',
    'DingTalkNotifier', 
    'AIService',
    'ClaudeService',
    'DeepSeekService',
    'GitService',
    'GitHubService',
    'GitLabService',
    'ServiceFactory'
]
