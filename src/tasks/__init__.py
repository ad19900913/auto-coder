"""
自动化AI任务执行系统 - 任务执行器模块
"""

__version__ = "1.0.0"
__author__ = "Auto Coder Team"
__description__ = "自动化AI任务执行系统任务执行器模块"

# 导入所有任务执行器
from .coding_executor import CodingTaskExecutor
from .review_executor import ReviewTaskExecutor
from .doc_executor import DocTaskExecutor
from .requirement_review_executor import RequirementReviewTaskExecutor
from .custom_executor import CustomTaskExecutor
from .intelligent_task_executor import IntelligentTaskExecutor
from .ai_model_management_executor import AIModelManagementExecutor
from .multimodal_ai_executor import MultimodalAIExecutor
from .machine_learning_executor import MachineLearningExecutor

__all__ = [
    'CodingTaskExecutor',
    'ReviewTaskExecutor',
    'DocTaskExecutor',
    'RequirementReviewTaskExecutor',
    'CustomTaskExecutor',
    'IntelligentTaskExecutor',
    'AIModelManagementExecutor',
    'MultimodalAIExecutor',
    'MachineLearningExecutor'
]
