"""
配置工具模块
提供配置相关的通用功能
"""

import os
import logging
from typing import Any, Dict, List, Optional, Union
from pathlib import Path


class ConfigUtils:
    """配置工具类"""
    
    @staticmethod
    def get_env_var(key: str, default: Optional[str] = None, 
                   required: bool = False) -> Optional[str]:
        """
        获取环境变量
        
        Args:
            key: 环境变量名
            default: 默认值
            required: 是否必需
            
        Returns:
            环境变量值
            
        Raises:
            ValueError: 必需的环境变量不存在
        """
        value = os.getenv(key, default)
        
        if required and value is None:
            raise ValueError(f"必需的环境变量 {key} 未设置")
        
        return value
    
    @staticmethod
    def expand_env_vars(text: str) -> str:
        """
        展开文本中的环境变量
        
        Args:
            text: 包含环境变量的文本
            
        Returns:
            展开后的文本
        """
        return os.path.expandvars(text)
    
    @staticmethod
    def get_config_path(config_name: str, 
                       config_dir: Union[str, Path] = "config") -> Path:
        """
        获取配置文件路径
        
        Args:
            config_name: 配置文件名
            config_dir: 配置目录
            
        Returns:
            配置文件路径
        """
        config_dir = Path(config_dir)
        
        # 支持多种扩展名
        extensions = ['.yaml', '.yml', '.json', '.toml']
        
        for ext in extensions:
            config_file = config_dir / f"{config_name}{ext}"
            if config_file.exists():
                return config_file
        
        # 如果都不存在，返回默认的yaml文件
        return config_dir / f"{config_name}.yaml"
    
    @staticmethod
    def validate_config_structure(config: Dict[str, Any], 
                               required_fields: List[str],
                               optional_fields: Optional[List[str]] = None) -> List[str]:
        """
        验证配置结构
        
        Args:
            config: 配置字典
            required_fields: 必需字段列表
            optional_fields: 可选字段列表
            
        Returns:
            错误信息列表
        """
        errors = []
        
        # 检查必需字段
        for field in required_fields:
            if field not in config:
                errors.append(f"缺少必需字段: {field}")
        
        # 检查未知字段
        if optional_fields:
            all_fields = set(required_fields + optional_fields)
            unknown_fields = set(config.keys()) - all_fields
            if unknown_fields:
                errors.append(f"未知字段: {', '.join(unknown_fields)}")
        
        return errors
    
    @staticmethod
    def merge_configs(base_config: Dict[str, Any], 
                     override_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        合并配置，override_config会覆盖base_config中的相同键
        
        Args:
            base_config: 基础配置
            override_config: 覆盖配置
            
        Returns:
            合并后的配置
        """
        merged = base_config.copy()
        
        for key, value in override_config.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = ConfigUtils.merge_configs(merged[key], value)
            else:
                merged[key] = value
        
        return merged
    
    @staticmethod
    def get_nested_config_value(config: Dict[str, Any], 
                               key_path: str, 
                               default: Any = None) -> Any:
        """
        获取嵌套配置值
        
        Args:
            config: 配置字典
            key_path: 键路径，用点分隔（如 'database.host'）
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key_path.split('.')
        current = config
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
    
    @staticmethod
    def set_nested_config_value(config: Dict[str, Any], 
                               key_path: str, 
                               value: Any) -> None:
        """
        设置嵌套配置值
        
        Args:
            config: 配置字典
            key_path: 键路径，用点分隔
            value: 要设置的值
        """
        keys = key_path.split('.')
        current = config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    @staticmethod
    def load_config_with_env_substitution(config_path: Union[str, Path]) -> Dict[str, Any]:
        """
        加载配置并进行环境变量替换
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            处理后的配置字典
        """
        from ..utils.file_utils import FileUtils
        
        config_path = Path(config_path)
        
        if config_path.suffix in ['.yaml', '.yml']:
            config = FileUtils.read_yaml_file(config_path)
        elif config_path.suffix == '.json':
            config = FileUtils.read_json_file(config_path)
        else:
            raise ValueError(f"不支持的配置文件格式: {config_path.suffix}")
        
        # 递归替换环境变量
        return ConfigUtils._substitute_env_vars_recursive(config)
    
    @staticmethod
    def _substitute_env_vars_recursive(data: Any) -> Any:
        """
        递归替换数据结构中的环境变量
        
        Args:
            data: 要处理的数据
            
        Returns:
            处理后的数据
        """
        if isinstance(data, dict):
            return {key: ConfigUtils._substitute_env_vars_recursive(value) 
                   for key, value in data.items()}
        elif isinstance(data, list):
            return [ConfigUtils._substitute_env_vars_recursive(item) 
                   for item in data]
        elif isinstance(data, str):
            return ConfigUtils.expand_env_vars(data)
        else:
            return data
    
    @staticmethod
    def create_config_template(template_path: Union[str, Path], 
                              config_structure: Dict[str, Any]) -> None:
        """
        创建配置模板文件
        
        Args:
            template_path: 模板文件路径
            config_structure: 配置结构
        """
        from ..utils.file_utils import FileUtils
        
        template_path = Path(template_path)
        
        # 添加注释
        template_content = {
            "# 配置模板": "请根据实际情况修改配置值",
            **config_structure
        }
        
        if template_path.suffix in ['.yaml', '.yml']:
            FileUtils.write_yaml_file(template_path, template_content)
        elif template_path.suffix == '.json':
            FileUtils.write_json_file(template_path, template_content)
        else:
            raise ValueError(f"不支持的模板文件格式: {template_path.suffix}")
    
    @staticmethod
    def validate_config_values(config: Dict[str, Any], 
                             validation_rules: Dict[str, Any]) -> List[str]:
        """
        验证配置值
        
        Args:
            config: 配置字典
            validation_rules: 验证规则字典
            
        Returns:
            错误信息列表
        """
        errors = []
        
        for field, rules in validation_rules.items():
            if field not in config:
                continue
            
            value = config[field]
            
            # 类型验证
            if 'type' in rules:
                expected_type = rules['type']
                if not isinstance(value, expected_type):
                    errors.append(f"字段 {field} 类型错误，期望 {expected_type.__name__}，实际 {type(value).__name__}")
            
            # 范围验证
            if 'min' in rules and isinstance(value, (int, float)):
                if value < rules['min']:
                    errors.append(f"字段 {field} 值 {value} 小于最小值 {rules['min']}")
            
            if 'max' in rules and isinstance(value, (int, float)):
                if value > rules['max']:
                    errors.append(f"字段 {field} 值 {value} 大于最大值 {rules['max']}")
            
            # 选项验证
            if 'choices' in rules:
                if value not in rules['choices']:
                    errors.append(f"字段 {field} 值 {value} 不在允许的选项中: {rules['choices']}")
            
            # 正则表达式验证
            if 'pattern' in rules and isinstance(value, str):
                import re
                if not re.match(rules['pattern'], value):
                    errors.append(f"字段 {field} 值 {value} 不符合模式 {rules['pattern']}")
        
        return errors
