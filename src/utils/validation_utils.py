"""
验证工具模块
提供数据验证和类型检查功能
"""

import re
import json
from typing import Any, Dict, List, Optional, Union, Type, Callable
from datetime import datetime
from pathlib import Path


class ValidationUtils:
    """验证工具类"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        验证邮箱地址
        
        Args:
            email: 邮箱地址
            
        Returns:
            是否有效
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """
        验证URL地址
        
        Args:
            url: URL地址
            
        Returns:
            是否有效
        """
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(pattern, url))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """
        验证手机号码（中国）
        
        Args:
            phone: 手机号码
            
        Returns:
            是否有效
        """
        pattern = r'^1[3-9]\d{9}$'
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def validate_ip_address(ip: str) -> bool:
        """
        验证IP地址
        
        Args:
            ip: IP地址
            
        Returns:
            是否有效
        """
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(pattern, ip):
            return False
        
        parts = ip.split('.')
        for part in parts:
            if not 0 <= int(part) <= 255:
                return False
        
        return True
    
    @staticmethod
    def validate_json_string(json_str: str) -> bool:
        """
        验证JSON字符串
        
        Args:
            json_str: JSON字符串
            
        Returns:
            是否有效
        """
        try:
            json.loads(json_str)
            return True
        except (json.JSONDecodeError, TypeError):
            return False
    
    @staticmethod
    def validate_file_path(file_path: Union[str, Path], 
                          must_exist: bool = True) -> bool:
        """
        验证文件路径
        
        Args:
            file_path: 文件路径
            must_exist: 是否必须存在
            
        Returns:
            是否有效
        """
        try:
            path = Path(file_path)
            if must_exist:
                return path.exists() and path.is_file()
            else:
                return path.parent.exists() or path.parent == Path('.')
        except (OSError, ValueError):
            return False
    
    @staticmethod
    def validate_directory_path(dir_path: Union[str, Path], 
                               must_exist: bool = True) -> bool:
        """
        验证目录路径
        
        Args:
            dir_path: 目录路径
            must_exist: 是否必须存在
            
        Returns:
            是否有效
        """
        try:
            path = Path(dir_path)
            if must_exist:
                return path.exists() and path.is_dir()
            else:
                return True  # 目录可以不存在
        except (OSError, ValueError):
            return False
    
    @staticmethod
    def validate_date_string(date_str: str, 
                           format_str: str = '%Y-%m-%d') -> bool:
        """
        验证日期字符串
        
        Args:
            date_str: 日期字符串
            format_str: 日期格式
            
        Returns:
            是否有效
        """
        try:
            datetime.strptime(date_str, format_str)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_range(value: Union[int, float], 
                      min_val: Optional[Union[int, float]] = None,
                      max_val: Optional[Union[int, float]] = None) -> bool:
        """
        验证数值范围
        
        Args:
            value: 要验证的值
            min_val: 最小值
            max_val: 最大值
            
        Returns:
            是否在范围内
        """
        if min_val is not None and value < min_val:
            return False
        if max_val is not None and value > max_val:
            return False
        return True
    
    @staticmethod
    def validate_length(value: str, 
                       min_length: Optional[int] = None,
                       max_length: Optional[int] = None) -> bool:
        """
        验证字符串长度
        
        Args:
            value: 要验证的字符串
            min_length: 最小长度
            max_length: 最大长度
            
        Returns:
            是否在长度范围内
        """
        length = len(value)
        if min_length is not None and length < min_length:
            return False
        if max_length is not None and length > max_length:
            return False
        return True
    
    @staticmethod
    def validate_choices(value: Any, choices: List[Any]) -> bool:
        """
        验证值是否在可选列表中
        
        Args:
            value: 要验证的值
            choices: 可选值列表
            
        Returns:
            是否在可选列表中
        """
        return value in choices
    
    @staticmethod
    def validate_pattern(value: str, pattern: str) -> bool:
        """
        验证字符串是否匹配正则表达式
        
        Args:
            value: 要验证的字符串
            pattern: 正则表达式模式
            
        Returns:
            是否匹配
        """
        try:
            return bool(re.match(pattern, value))
        except re.error:
            return False
    
    @staticmethod
    def validate_type(value: Any, expected_type: Type) -> bool:
        """
        验证值的类型
        
        Args:
            value: 要验证的值
            expected_type: 期望的类型
            
        Returns:
            类型是否正确
        """
        return isinstance(value, expected_type)
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], 
                                required_fields: List[str]) -> List[str]:
        """
        验证必需字段
        
        Args:
            data: 数据字典
            required_fields: 必需字段列表
            
        Returns:
            缺失字段列表
        """
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)
        return missing_fields
    
    @staticmethod
    def validate_data_structure(data: Dict[str, Any], 
                               schema: Dict[str, Any]) -> List[str]:
        """
        验证数据结构
        
        Args:
            data: 要验证的数据
            schema: 验证模式
            
        Returns:
            错误信息列表
        """
        errors = []
        
        for field, rules in schema.items():
            if field not in data:
                if rules.get('required', False):
                    errors.append(f"缺少必需字段: {field}")
                continue
            
            value = data[field]
            field_errors = ValidationUtils._validate_field(value, rules, field)
            errors.extend(field_errors)
        
        return errors
    
    @staticmethod
    def _validate_field(value: Any, rules: Dict[str, Any], 
                       field_name: str) -> List[str]:
        """
        验证单个字段
        
        Args:
            value: 字段值
            rules: 验证规则
            field_name: 字段名
            
        Returns:
            错误信息列表
        """
        errors = []
        
        # 类型验证
        if 'type' in rules:
            expected_type = rules['type']
            if not isinstance(value, expected_type):
                errors.append(f"字段 {field_name} 类型错误，期望 {expected_type.__name__}")
        
        # 字符串验证
        if isinstance(value, str):
            if 'min_length' in rules:
                if len(value) < rules['min_length']:
                    errors.append(f"字段 {field_name} 长度过短")
            
            if 'max_length' in rules:
                if len(value) > rules['max_length']:
                    errors.append(f"字段 {field_name} 长度过长")
            
            if 'pattern' in rules:
                if not ValidationUtils.validate_pattern(value, rules['pattern']):
                    errors.append(f"字段 {field_name} 格式不正确")
        
        # 数值验证
        if isinstance(value, (int, float)):
            if 'min' in rules:
                if value < rules['min']:
                    errors.append(f"字段 {field_name} 值过小")
            
            if 'max' in rules:
                if value > rules['max']:
                    errors.append(f"字段 {field_name} 值过大")
        
        # 选择验证
        if 'choices' in rules:
            if value not in rules['choices']:
                errors.append(f"字段 {field_name} 值不在允许的选项中")
        
        # 自定义验证
        if 'validator' in rules:
            validator = rules['validator']
            if callable(validator):
                try:
                    if not validator(value):
                        errors.append(f"字段 {field_name} 自定义验证失败")
                except Exception as e:
                    errors.append(f"字段 {field_name} 自定义验证出错: {str(e)}")
        
        return errors
    
    @staticmethod
    def create_validator(validation_rules: Dict[str, Any]) -> Callable[[Dict[str, Any]], List[str]]:
        """
        创建验证器函数
        
        Args:
            validation_rules: 验证规则
            
        Returns:
            验证器函数
        """
        def validator(data: Dict[str, Any]) -> List[str]:
            return ValidationUtils.validate_data_structure(data, validation_rules)
        
        return validator
    
    @staticmethod
    def sanitize_string(value: str, 
                       max_length: Optional[int] = None,
                       allowed_chars: Optional[str] = None) -> str:
        """
        清理字符串
        
        Args:
            value: 要清理的字符串
            max_length: 最大长度
            allowed_chars: 允许的字符（正则表达式）
            
        Returns:
            清理后的字符串
        """
        # 去除首尾空白
        cleaned = value.strip()
        
        # 限制长度
        if max_length is not None:
            cleaned = cleaned[:max_length]
        
        # 过滤字符
        if allowed_chars is not None:
            cleaned = re.sub(f'[^{allowed_chars}]', '', cleaned)
        
        return cleaned
    
    @staticmethod
    def validate_config_file(config_path: Union[str, Path], 
                           schema: Dict[str, Any]) -> List[str]:
        """
        验证配置文件
        
        Args:
            config_path: 配置文件路径
            schema: 验证模式
            
        Returns:
            错误信息列表
        """
        errors = []
        
        try:
            from ..utils.file_utils import FileUtils
            
            config_path = Path(config_path)
            
            if config_path.suffix in ['.yaml', '.yml']:
                config = FileUtils.read_yaml_file(config_path)
            elif config_path.suffix == '.json':
                config = FileUtils.read_json_file(config_path)
            else:
                errors.append(f"不支持的配置文件格式: {config_path.suffix}")
                return errors
            
            validation_errors = ValidationUtils.validate_data_structure(config, schema)
            errors.extend(validation_errors)
            
        except Exception as e:
            errors.append(f"配置文件验证失败: {str(e)}")
        
        return errors
