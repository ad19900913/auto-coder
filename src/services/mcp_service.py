"""
MCP服务模块 - 支持Model Context Protocol服务
"""

import logging
import json
import asyncio
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
import subprocess
import os
import tempfile


class MCPService:
    """MCP服务类，支持Model Context Protocol服务"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化MCP服务
        
        Args:
            config: MCP服务配置
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        self.mcp_servers = {}
        self.available_tools = {}
        
        # 如果提供了配置，自动加载MCP服务
        if self.config:
            self._load_services_from_config()
    
    def _load_services_from_config(self):
        """
        从配置中自动加载MCP服务
        """
        try:
            # 加载MCP服务配置
            mcp_services = self.config.get('mcp_services', {})
            
            for server_name, server_config in mcp_services.items():
                # 检查服务是否启用
                if server_config.get('enabled', True):
                    self.register_mcp_server(server_name, server_config)
                    self.logger.info(f"自动加载MCP服务: {server_name}")
                else:
                    self.logger.info(f"跳过禁用的MCP服务: {server_name}")
            
            # 加载MCP工具配置
            mcp_tools = self.config.get('mcp_tools', {})
            
            # 处理默认工具
            default_tools = mcp_tools.get('default_tools', [])
            for tool_path in default_tools:
                if '.' in tool_path:
                    server_name, tool_name = tool_path.split('.', 1)
                    if server_name in self.mcp_servers:
                        self.logger.info(f"注册默认工具: {tool_path}")
            
            # 处理自定义工具
            custom_tools = mcp_tools.get('custom_tools', {})
            for tool_name, tool_config in custom_tools.items():
                self.logger.info(f"注册自定义工具: {tool_name}")
            
            self.logger.info(f"MCP服务自动加载完成，共加载 {len(self.mcp_servers)} 个服务")
            
        except Exception as e:
            self.logger.error(f"自动加载MCP服务失败: {e}")
    
    def register_mcp_server(self, server_name: str, server_config: Dict[str, Any]):
        """
        注册MCP服务器
        
        Args:
            server_name: 服务器名称
            server_config: 服务器配置
        """
        try:
            self.mcp_servers[server_name] = {
                'config': server_config,
                'tools': [],
                'status': 'registered'
            }
            self.logger.info(f"MCP服务器注册成功: {server_name}")
        except Exception as e:
            self.logger.error(f"MCP服务器注册失败 {server_name}: {e}")
    
    def discover_tools(self, server_name: str) -> List[Dict[str, Any]]:
        """
        发现MCP服务器的工具
        
        Args:
            server_name: 服务器名称
            
        Returns:
            工具列表
        """
        try:
            if server_name not in self.mcp_servers:
                raise ValueError(f"MCP服务器未注册: {server_name}")
            
            server_config = self.mcp_servers[server_name]['config']
            tools = self._call_mcp_server(server_name, 'list_tools', {})
            
            self.mcp_servers[server_name]['tools'] = tools
            self.available_tools[server_name] = tools
            
            self.logger.info(f"发现MCP工具 {server_name}: {len(tools)} 个工具")
            return tools
            
        except Exception as e:
            self.logger.error(f"发现MCP工具失败 {server_name}: {e}")
            return []
    
    def call_tool(self, server_name: str, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """
        调用MCP工具
        
        Args:
            server_name: 服务器名称
            tool_name: 工具名称
            parameters: 工具参数
            
        Returns:
            工具执行结果
        """
        try:
            if server_name not in self.mcp_servers:
                raise ValueError(f"MCP服务器未注册: {server_name}")
            
            result = self._call_mcp_server(server_name, 'call_tool', {
                'tool_name': tool_name,
                'parameters': parameters
            })
            
            self.logger.info(f"MCP工具调用成功: {server_name}.{tool_name}")
            return result
            
        except Exception as e:
            self.logger.error(f"MCP工具调用失败 {server_name}.{tool_name}: {e}")
            raise
    
    def _call_mcp_server(self, server_name: str, method: str, params: Dict[str, Any]) -> Any:
        """
        调用MCP服务器方法
        
        Args:
            server_name: 服务器名称
            method: 方法名
            params: 参数
            
        Returns:
            执行结果
        """
        # 这里实现具体的MCP服务器调用逻辑
        # 可以使用subprocess、HTTP请求或其他方式
        server_config = self.mcp_servers[server_name]['config']
        
        if method == 'list_tools':
            return self._list_tools_implementation(server_config)
        elif method == 'call_tool':
            return self._call_tool_implementation(server_config, params)
        else:
            raise ValueError(f"不支持的MCP方法: {method}")
    
    def _list_tools_implementation(self, server_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """实现工具列表获取"""
        # 这里可以根据不同的MCP服务器类型实现具体的工具发现逻辑
        tools = []
        
        # 示例：文件系统工具
        if server_config.get('type') == 'filesystem':
            tools.extend([
                {
                    'name': 'read_file',
                    'description': '读取文件内容',
                    'parameters': {
                        'path': {'type': 'string', 'description': '文件路径'}
                    }
                },
                {
                    'name': 'write_file',
                    'description': '写入文件内容',
                    'parameters': {
                        'path': {'type': 'string', 'description': '文件路径'},
                        'content': {'type': 'string', 'description': '文件内容'}
                    }
                },
                {
                    'name': 'list_directory',
                    'description': '列出目录内容',
                    'parameters': {
                        'path': {'type': 'string', 'description': '目录路径'}
                    }
                }
            ])
        
        # 示例：数据库工具
        elif server_config.get('type') == 'database':
            tools.extend([
                {
                    'name': 'query_database',
                    'description': '执行数据库查询',
                    'parameters': {
                        'query': {'type': 'string', 'description': 'SQL查询语句'}
                    }
                },
                {
                    'name': 'execute_sql',
                    'description': '执行SQL语句',
                    'parameters': {
                        'sql': {'type': 'string', 'description': 'SQL语句'}
                    }
                }
            ])
        
        return tools
    
    def _call_tool_implementation(self, server_config: Dict[str, Any], params: Dict[str, Any]) -> Any:
        """实现工具调用"""
        tool_name = params.get('tool_name')
        parameters = params.get('parameters', {})
        
        if server_config.get('type') == 'filesystem':
            return self._call_filesystem_tool(tool_name, parameters)
        elif server_config.get('type') == 'database':
            return self._call_database_tool(tool_name, parameters)
        else:
            return {'error': f'不支持的MCP服务器类型: {server_config.get("type")}'}
    
    def _call_filesystem_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """调用文件系统工具"""
        try:
            if tool_name == 'read_file':
                path = parameters.get('path')
                if not path or not os.path.exists(path):
                    return {'error': f'文件不存在: {path}'}
                
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {'content': content, 'path': path}
            
            elif tool_name == 'write_file':
                path = parameters.get('path')
                content = parameters.get('content', '')
                
                # 确保目录存在
                os.makedirs(os.path.dirname(path), exist_ok=True)
                
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return {'success': True, 'path': path}
            
            elif tool_name == 'list_directory':
                path = parameters.get('path', '.')
                if not os.path.exists(path):
                    return {'error': f'目录不存在: {path}'}
                
                items = []
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    items.append({
                        'name': item,
                        'path': item_path,
                        'type': 'directory' if os.path.isdir(item_path) else 'file',
                        'size': os.path.getsize(item_path) if os.path.isfile(item_path) else None
                    })
                
                return {'items': items, 'path': path}
            
            else:
                return {'error': f'不支持的文件系统工具: {tool_name}'}
                
        except Exception as e:
            return {'error': f'文件系统工具调用失败: {e}'}
    
    def _call_database_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """调用数据库工具"""
        # 这里实现数据库工具调用
        # 需要根据具体的数据库配置来实现
        return {'error': '数据库工具暂未实现'}
    
    def get_available_tools(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取所有可用的MCP工具
        
        Returns:
            工具字典，键为服务器名称，值为工具列表
        """
        return self.available_tools.copy()
    
    def get_tool_description(self, server_name: str, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        获取工具描述
        
        Args:
            server_name: 服务器名称
            tool_name: 工具名称
            
        Returns:
            工具描述
        """
        if server_name in self.available_tools:
            for tool in self.available_tools[server_name]:
                if tool.get('name') == tool_name:
                    return tool
        return None
    
    def validate_tool_parameters(self, server_name: str, tool_name: str, parameters: Dict[str, Any]) -> List[str]:
        """
        验证工具参数
        
        Args:
            server_name: 服务器名称
            tool_name: 工具名称
            parameters: 参数
            
        Returns:
            验证错误列表
        """
        errors = []
        tool_desc = self.get_tool_description(server_name, tool_name)
        
        if not tool_desc:
            errors.append(f"工具不存在: {server_name}.{tool_name}")
            return errors
        
        required_params = tool_desc.get('parameters', {})
        for param_name, param_desc in required_params.items():
            if param_name not in parameters:
                errors.append(f"缺少必需参数: {param_name}")
        
        return errors


class MCPToolManager:
    """MCP工具管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.mcp_service = MCPService()
        self.tool_cache = {}
        
    def register_tool(self, tool_name: str, tool_function: Callable, description: str = ""):
        """
        注册自定义工具
        
        Args:
            tool_name: 工具名称
            tool_function: 工具函数
            description: 工具描述
        """
        self.tool_cache[tool_name] = {
            'function': tool_function,
            'description': description
        }
        self.logger.info(f"自定义工具注册成功: {tool_name}")
    
    def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """
        调用工具
        
        Args:
            tool_name: 工具名称
            parameters: 工具参数
            
        Returns:
            执行结果
        """
        try:
            if tool_name in self.tool_cache:
                # 调用自定义工具
                tool_func = self.tool_cache[tool_name]['function']
                return tool_func(**parameters)
            else:
                # 尝试调用MCP工具
                # 解析工具名称格式: server_name.tool_name
                if '.' in tool_name:
                    server_name, mcp_tool_name = tool_name.split('.', 1)
                    return self.mcp_service.call_tool(server_name, mcp_tool_name, parameters)
                else:
                    return {'error': f'工具不存在: {tool_name}'}
                    
        except Exception as e:
            self.logger.error(f"工具调用失败 {tool_name}: {e}")
            return {'error': str(e)}
    
    def list_all_tools(self) -> Dict[str, Any]:
        """
        列出所有可用工具
        
        Returns:
            工具信息字典
        """
        tools = {
            'custom_tools': {},
            'mcp_tools': self.mcp_service.get_available_tools()
        }
        
        # 添加自定义工具信息
        for tool_name, tool_info in self.tool_cache.items():
            tools['custom_tools'][tool_name] = {
                'description': tool_info['description'],
                'type': 'custom'
            }
        
        return tools
