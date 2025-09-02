"""
自定义异常类 - 定义系统特定的异常类型
"""


class AutoCoderError(Exception):
    """自动化AI任务执行系统基础异常类"""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        """
        初始化异常
        
        Args:
            message: 错误消息
            error_code: 错误代码
            details: 错误详情
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class ConfigError(AutoCoderError):
    """配置相关异常"""
    pass


class TaskError(AutoCoderError):
    """任务执行相关异常"""
    pass


class WorkflowError(AutoCoderError):
    """工作流相关异常"""
    pass


class AIServiceError(AutoCoderError):
    """AI服务相关异常"""
    pass


class GitServiceError(AutoCoderError):
    """Git服务相关异常"""
    pass


class NotificationError(AutoCoderError):
    """通知服务相关异常"""
    pass


class StateError(AutoCoderError):
    """状态管理相关异常"""
    pass


class ValidationError(AutoCoderError):
    """验证相关异常"""
    pass


class TimeoutError(AutoCoderError):
    """超时相关异常"""
    pass


class RetryError(AutoCoderError):
    """重试相关异常"""
    pass
