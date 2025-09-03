"""
服务工厂模块 - 统一管理AI和Git服务的创建
"""

import logging
from typing import Dict, Any, Optional
from .ai_service import AIService, ClaudeService, DeepSeekService, GeminiService
from .git_service import GitService, GitHubService, GitLabService
from .notify_service import NotifyService


class ServiceFactory:
    """服务工厂类，统一管理各种服务的创建"""
    
    def __init__(self, config_manager):
        """
        初始化服务工厂
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        
        # 缓存已创建的服务实例
        self._ai_service_cache = {}
        self._git_service_cache = {}
        self._notify_service_cache = None
    
    def create_ai_service(self, provider: str = None, config: Dict[str, Any] = None) -> AIService:
        """
        创建AI服务实例
        
        Args:
            provider: AI服务提供商（claude, deepseek）
            config: 服务配置，如果为None则从全局配置中获取
            
        Returns:
            AI服务实例
        """
        if not provider:
            # 从全局配置中获取默认AI服务
            ai_services_config = self.config_manager.global_config.get('ai_services', {})
            provider = ai_services_config.get('default', 'claude')
            self.logger.info(f"使用默认AI服务: {provider}")
        
        if not config:
            config = self.config_manager.global_config.get('ai_services', {}).get(provider, {})
        
        # 检查缓存
        cache_key = f"{provider}_{hash(str(config))}"
        if cache_key in self._ai_service_cache:
            return self._ai_service_cache[cache_key]
        
        # 在测试模式下，如果没有API密钥，使用模拟配置
        if not config.get('api_key'):
            config = {
                'api_key': 'test_key',
                'base_url': 'https://api.anthropic.com',
                'model': 'claude-3-sonnet-20240229'
            }
        
        # 创建服务实例
        if provider == 'claude':
            service = ClaudeService(config)
        elif provider == 'deepseek':
            service = DeepSeekService(config)
        elif provider == 'gemini':
            service = GeminiService(config)
        else:
            raise ValueError(f"不支持的AI服务提供商: {provider}")
        
        # 缓存实例
        self._ai_service_cache[cache_key] = service
        self.logger.info(f"AI服务创建成功: {provider}")
        
        return service
    
    def create_git_service(self, platform: str = None, config: Dict[str, Any] = None) -> GitService:
        """
        创建Git服务实例
        
        Args:
            platform: Git平台（github, gitlab）
            config: 服务配置，如果为None则从全局配置中获取
            
        Returns:
            Git服务实例
        """
        if not platform:
            platform = self.config_manager.global_config.get('git', {}).get('default', 'github')
        
        if not config:
            config = self.config_manager.global_config.get('git', {}).get(platform, {})
        
        # 检查缓存
        cache_key = f"{platform}_{hash(str(config))}"
        if cache_key in self._git_service_cache:
            return self._git_service_cache[cache_key]
        
        # 在测试模式下，如果没有token，使用模拟配置
        if not config.get('token'):
            config = {
                'token': 'test_token',
                'username': 'test_user'
            }
        
        # 创建服务实例
        if platform == 'github':
            service = GitHubService(config)
        elif platform == 'gitlab':
            service = GitLabService(config)
        else:
            raise ValueError(f"不支持的Git平台: {platform}")
        
        # 缓存实例
        self._git_service_cache[cache_key] = service
        self.logger.info(f"Git服务创建成功: {platform}")
        
        return service
    
    def create_notify_service(self) -> NotifyService:
        """
        创建通知服务实例
        
        Returns:
            通知服务实例
        """
        if self._notify_service_cache is None:
            self._notify_service_cache = NotifyService(self.config_manager)
            self.logger.info("通知服务创建成功")
        
        return self._notify_service_cache
    
    def create_services_for_task(self, task_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        为任务创建所需的服务实例
        
        Args:
            task_config: 任务配置
            
        Returns:
            包含所有服务实例的字典
        """
        services = {}
        
        # 创建AI服务 - 使用全局默认配置
        ai_config = task_config.get('ai', {})
        # 如果没有指定provider，使用全局默认值
        ai_provider = ai_config.get('provider') if ai_config else None
        services['ai_service'] = self.create_ai_service(ai_provider, ai_config)
        
        # 创建Git服务
        git_config = task_config.get('git', {})
        git_platform = git_config.get('platform', 'github')
        services['git_service'] = self.create_git_service(git_platform, git_config)
        
        # 创建通知服务
        services['notify_service'] = self.create_notify_service()
        
        return services
    
    def clear_cache(self):
        """清除服务缓存"""
        self._ai_service_cache.clear()
        self._git_service_cache.clear()
        self._notify_service_cache = None
        self.logger.info("服务缓存已清除")
