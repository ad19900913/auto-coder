"""
文件操作工具模块
提供常用的文件操作功能
"""

import os
import json
import yaml
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime


class FileUtils:
    """文件操作工具类"""
    
    @staticmethod
    def ensure_directory_exists(directory_path: Union[str, Path]) -> None:
        """
        确保目录存在，如果不存在则创建
        
        Args:
            directory_path: 目录路径
        """
        path = Path(directory_path)
        path.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def safe_write_file(file_path: Union[str, Path], content: str, 
                       encoding: str = 'utf-8', backup: bool = False) -> None:
        """
        安全写入文件，支持备份
        
        Args:
            file_path: 文件路径
            content: 文件内容
            encoding: 编码格式
            backup: 是否备份原文件
        """
        file_path = Path(file_path)
        
        # 确保目录存在
        FileUtils.ensure_directory_exists(file_path.parent)
        
        # 备份原文件
        if backup and file_path.exists():
            backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
            file_path.rename(backup_path)
        
        # 写入文件
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
    
    @staticmethod
    def safe_read_file(file_path: Union[str, Path], 
                      encoding: str = 'utf-8') -> str:
        """
        安全读取文件
        
        Args:
            file_path: 文件路径
            encoding: 编码格式
            
        Returns:
            文件内容
            
        Raises:
            FileNotFoundError: 文件不存在
            UnicodeDecodeError: 编码错误
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    
    @staticmethod
    def write_json_file(file_path: Union[str, Path], data: Any, 
                       indent: int = 2, ensure_ascii: bool = False) -> None:
        """
        写入JSON文件
        
        Args:
            file_path: 文件路径
            data: 要写入的数据
            indent: 缩进空格数
            ensure_ascii: 是否确保ASCII编码
        """
        content = json.dumps(data, ensure_ascii=ensure_ascii, indent=indent)
        FileUtils.safe_write_file(file_path, content)
    
    @staticmethod
    def read_json_file(file_path: Union[str, Path]) -> Any:
        """
        读取JSON文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            JSON数据
        """
        content = FileUtils.safe_read_file(file_path)
        return json.loads(content)
    
    @staticmethod
    def write_yaml_file(file_path: Union[str, Path], data: Any, 
                       default_flow_style: bool = False, 
                       allow_unicode: bool = True) -> None:
        """
        写入YAML文件
        
        Args:
            file_path: 文件路径
            data: 要写入的数据
            default_flow_style: 是否使用流式风格
            allow_unicode: 是否允许Unicode
        """
        content = yaml.dump(data, default_flow_style=default_flow_style, 
                           allow_unicode=allow_unicode)
        FileUtils.safe_write_file(file_path, content)
    
    @staticmethod
    def read_yaml_file(file_path: Union[str, Path]) -> Any:
        """
        读取YAML文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            YAML数据
        """
        content = FileUtils.safe_read_file(file_path)
        return yaml.safe_load(content)
    
    @staticmethod
    def get_file_size(file_path: Union[str, Path]) -> int:
        """
        获取文件大小
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件大小（字节）
        """
        return Path(file_path).stat().st_size
    
    @staticmethod
    def get_file_modified_time(file_path: Union[str, Path]) -> datetime:
        """
        获取文件修改时间
        
        Args:
            file_path: 文件路径
            
        Returns:
            修改时间
        """
        timestamp = Path(file_path).stat().st_mtime
        return datetime.fromtimestamp(timestamp)
    
    @staticmethod
    def find_files_by_pattern(directory: Union[str, Path], 
                            pattern: str) -> List[Path]:
        """
        根据模式查找文件
        
        Args:
            directory: 搜索目录
            pattern: 文件模式（如*.py）
            
        Returns:
            匹配的文件路径列表
        """
        directory = Path(directory)
        return list(directory.rglob(pattern))
    
    @staticmethod
    def clean_directory(directory: Union[str, Path], 
                       keep_patterns: Optional[List[str]] = None) -> None:
        """
        清理目录，删除不需要的文件
        
        Args:
            directory: 目录路径
            keep_patterns: 要保留的文件模式列表
        """
        directory = Path(directory)
        
        if not directory.exists():
            return
        
        keep_patterns = keep_patterns or []
        
        for file_path in directory.iterdir():
            should_keep = False
            
            for pattern in keep_patterns:
                if file_path.match(pattern):
                    should_keep = True
                    break
            
            if not should_keep:
                if file_path.is_file():
                    file_path.unlink()
                elif file_path.is_dir():
                    FileUtils.clean_directory(file_path, keep_patterns)
                    if not any(file_path.iterdir()):
                        file_path.rmdir()
    
    @staticmethod
    def copy_file(source: Union[str, Path], destination: Union[str, Path]) -> None:
        """
        复制文件
        
        Args:
            source: 源文件路径
            destination: 目标文件路径
        """
        import shutil
        
        source = Path(source)
        destination = Path(destination)
        
        # 确保目标目录存在
        FileUtils.ensure_directory_exists(destination.parent)
        
        shutil.copy2(source, destination)
    
    @staticmethod
    def move_file(source: Union[str, Path], destination: Union[str, Path]) -> None:
        """
        移动文件
        
        Args:
            source: 源文件路径
            destination: 目标文件路径
        """
        import shutil
        
        source = Path(source)
        destination = Path(destination)
        
        # 确保目标目录存在
        FileUtils.ensure_directory_exists(destination.parent)
        
        shutil.move(str(source), str(destination))
