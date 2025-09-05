"""
日志工具模块
提供统一的日志配置和管理功能
"""

import logging
import sys
from typing import Optional, Dict, Any
from pathlib import Path
import colorlog


class LoggingUtils:
    """日志工具类"""
    
    # 日志级别映射
    LEVEL_MAPPING = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    @staticmethod
    def setup_logging(log_level: str = 'INFO', 
                     log_file: Optional[str] = None,
                     log_format: Optional[str] = None,
                     use_colors: bool = True) -> None:
        """
        设置日志配置
        
        Args:
            log_level: 日志级别
            log_file: 日志文件路径
            log_format: 日志格式
            use_colors: 是否使用颜色
        """
        # 清除现有的处理器
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # 设置日志级别
        level = LoggingUtils.LEVEL_MAPPING.get(log_level.upper(), logging.INFO)
        root_logger.setLevel(level)
        
        # 设置日志格式
        if log_format is None:
            log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        if use_colors:
            # 使用彩色日志
            color_formatter = colorlog.ColoredFormatter(
                '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white',
                }
            )
            console_handler.setFormatter(color_formatter)
        else:
            formatter = logging.Formatter(log_format, datefmt='%Y-%m-%d %H:%M:%S')
            console_handler.setFormatter(formatter)
        
        root_logger.addHandler(console_handler)
        
        # 文件处理器
        if log_file:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(level)
            file_formatter = logging.Formatter(log_format, datefmt='%Y-%m-%d %H:%M:%S')
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """
        获取指定名称的日志器
        
        Args:
            name: 日志器名称
            
        Returns:
            日志器实例
        """
        return logging.getLogger(name)
    
    @staticmethod
    def set_logger_level(logger_name: str, level: str) -> None:
        """
        设置指定日志器的级别
        
        Args:
            logger_name: 日志器名称
            level: 日志级别
        """
        logger = logging.getLogger(logger_name)
        log_level = LoggingUtils.LEVEL_MAPPING.get(level.upper(), logging.INFO)
        logger.setLevel(log_level)
    
    @staticmethod
    def add_file_handler(logger_name: str, file_path: str, 
                        level: str = 'INFO') -> None:
        """
        为指定日志器添加文件处理器
        
        Args:
            logger_name: 日志器名称
            file_path: 日志文件路径
            level: 日志级别
        """
        logger = logging.getLogger(logger_name)
        file_handler = logging.FileHandler(file_path, encoding='utf-8')
        file_handler.setLevel(LoggingUtils.LEVEL_MAPPING.get(level.upper(), logging.INFO))
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    @staticmethod
    def log_function_call(func_name: str, args: Dict[str, Any], 
                         logger: Optional[logging.Logger] = None) -> None:
        """
        记录函数调用
        
        Args:
            func_name: 函数名称
            args: 函数参数
            logger: 日志器，如果为None则使用默认日志器
        """
        if logger is None:
            logger = logging.getLogger(__name__)
        
        logger.debug(f"调用函数 {func_name}，参数: {args}")
    
    @staticmethod
    def log_execution_time(func_name: str, execution_time: float,
                          logger: Optional[logging.Logger] = None) -> None:
        """
        记录函数执行时间
        
        Args:
            func_name: 函数名称
            execution_time: 执行时间（秒）
            logger: 日志器，如果为None则使用默认日志器
        """
        if logger is None:
            logger = logging.getLogger(__name__)
        
        logger.info(f"函数 {func_name} 执行时间: {execution_time:.3f}秒")
    
    @staticmethod
    def log_error_with_context(error: Exception, context: Dict[str, Any],
                              logger: Optional[logging.Logger] = None) -> None:
        """
        记录带上下文的错误
        
        Args:
            error: 异常对象
            context: 错误上下文
            logger: 日志器，如果为None则使用默认日志器
        """
        if logger is None:
            logger = logging.getLogger(__name__)
        
        logger.error(f"错误: {str(error)}，上下文: {context}")
    
    @staticmethod
    def create_rotating_file_handler(file_path: str, 
                                   max_bytes: int = 10 * 1024 * 1024,  # 10MB
                                   backup_count: int = 5,
                                   level: str = 'INFO') -> logging.Handler:
        """
        创建轮转文件处理器
        
        Args:
            file_path: 日志文件路径
            max_bytes: 最大文件大小
            backup_count: 备份文件数量
            level: 日志级别
            
        Returns:
            轮转文件处理器
        """
        from logging.handlers import RotatingFileHandler
        
        handler = RotatingFileHandler(
            file_path, 
            maxBytes=max_bytes, 
            backupCount=backup_count,
            encoding='utf-8'
        )
        handler.setLevel(LoggingUtils.LEVEL_MAPPING.get(level.upper(), logging.INFO))
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        return handler
    
    @staticmethod
    def create_timed_rotating_file_handler(file_path: str,
                                         when: str = 'midnight',
                                         interval: int = 1,
                                         backup_count: int = 30,
                                         level: str = 'INFO') -> logging.Handler:
        """
        创建时间轮转文件处理器
        
        Args:
            file_path: 日志文件路径
            when: 轮转时间点
            interval: 轮转间隔
            backup_count: 备份文件数量
            level: 日志级别
            
        Returns:
            时间轮转文件处理器
        """
        from logging.handlers import TimedRotatingFileHandler
        
        handler = TimedRotatingFileHandler(
            file_path,
            when=when,
            interval=interval,
            backupCount=backup_count,
            encoding='utf-8'
        )
        handler.setLevel(LoggingUtils.LEVEL_MAPPING.get(level.upper(), logging.INFO))
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        return handler
    
    @staticmethod
    def setup_structured_logging(log_file: Optional[str] = None) -> None:
        """
        设置结构化日志（JSON格式）
        
        Args:
            log_file: 日志文件路径
        """
        import json
        
        class StructuredFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    'timestamp': self.formatTime(record),
                    'level': record.levelname,
                    'logger': record.name,
                    'message': record.getMessage(),
                    'module': record.module,
                    'function': record.funcName,
                    'line': record.lineno
                }
                
                if record.exc_info:
                    log_entry['exception'] = self.formatException(record.exc_info)
                
                return json.dumps(log_entry, ensure_ascii=False)
        
        # 清除现有处理器
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # 设置结构化处理器
        if log_file:
            handler = logging.FileHandler(log_file, encoding='utf-8')
        else:
            handler = logging.StreamHandler(sys.stdout)
        
        handler.setFormatter(StructuredFormatter())
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.INFO)
