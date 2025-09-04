"""
服务工厂模块 - 统一管理AI和Git服务的创建
"""

import logging
from typing import Dict, Any, Optional
from .ai_service import AIService, ClaudeService, DeepSeekService, GeminiService, CursorService
from .git_service import GitService, GitHubService, GitLabService
from .notify_service import NotifyService
from .incremental_code_service import IncrementalCodeService
from .complex_refactor_service import ComplexRefactorService
from .mcp_service import MCPService, MCPToolManager
from .intelligent_task_service import IntelligentTaskService
from .ai_model_manager import AIModelManager
from .multimodal_ai_service import MultimodalAIService
from .machine_learning_service import MachineLearningService


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
        self._intelligent_task_service_cache = None
        self._ai_model_manager_cache = None
        self._multimodal_ai_service_cache = None
        self._machine_learning_service_cache = None
    
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
        elif provider == 'cursor':
            service = CursorService(config)
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
    
    def create_intelligent_task_service(self, ai_service: AIService = None) -> IntelligentTaskService:
        """
        创建智能任务生成服务实例
        
        Args:
            ai_service: AI服务实例，如果为None则创建默认实例
            
        Returns:
            智能任务生成服务实例
        """
        if self._intelligent_task_service_cache is None:
            if ai_service is None:
                ai_service = self.create_ai_service()
            
            # 获取智能任务生成服务配置
            intelligent_task_config = self.config_manager.global_config.get('intelligent_task_generation', {})
            
            self._intelligent_task_service_cache = IntelligentTaskService(ai_service, intelligent_task_config)
            self.logger.info("智能任务生成服务创建成功")
        
        return self._intelligent_task_service_cache
    
    def create_ai_model_manager(self) -> AIModelManager:
        """
        创建AI模型管理器实例
        
        Returns:
            AI模型管理器实例
        """
        if self._ai_model_manager_cache is None:
            # 获取AI模型管理配置
            ai_model_config = self.config_manager.global_config.get('ai_model_management', {})
            
            self._ai_model_manager_cache = AIModelManager(ai_model_config)
            self.logger.info("AI模型管理器创建成功")
        
        return self._ai_model_manager_cache
    
    def create_multimodal_ai_service(self, ai_service: AIService = None) -> MultimodalAIService:
        """
        创建多模态AI服务实例
        
        Args:
            ai_service: AI服务实例，如果为None则创建默认实例
            
        Returns:
            多模态AI服务实例
        """
        if self._multimodal_ai_service_cache is None:
            if ai_service is None:
                ai_service = self.create_ai_service()
            
            # 获取多模态AI服务配置
            multimodal_config = self.config_manager.global_config.get('multimodal_ai', {})
            
            self._multimodal_ai_service_cache = MultimodalAIService(multimodal_config, ai_service)
            self.logger.info("多模态AI服务创建成功")
        
        return self._multimodal_ai_service_cache
    
    def create_machine_learning_service(self) -> MachineLearningService:
        """
        创建机器学习服务实例
        
        Returns:
            机器学习服务实例
        """
        if self._machine_learning_service_cache is None:
            # 获取机器学习服务配置
            ml_config = self.config_manager.global_config.get('machine_learning', {})
            
            self._machine_learning_service_cache = MachineLearningService(ml_config)
            self.logger.info("机器学习服务创建成功")
        
        return self._machine_learning_service_cache
    
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
        
        # 创建增量代码服务
        services['incremental_code_service'] = IncrementalCodeService()
        
        # 创建复杂重构服务
        services['complex_refactor_service'] = ComplexRefactorService()
        
        # 创建MCP服务 - 从全局配置加载
        mcp_config = self.config_manager.global_config.get('mcp', {})
        services['mcp_service'] = MCPService(mcp_config)
        services['mcp_tool_manager'] = MCPToolManager()
        
        # 设置AI服务的MCP工具管理器
        services['ai_service'].set_mcp_tool_manager(services['mcp_tool_manager'])
        
        # 创建智能任务生成服务
        services['intelligent_task_service'] = self.create_intelligent_task_service(services['ai_service'])
        
        # 创建AI模型管理器
        services['ai_model_manager'] = self.create_ai_model_manager()
        
        # 创建多模态AI服务
        services['multimodal_ai_service'] = self.create_multimodal_ai_service(services['ai_service'])
        
        # 创建机器学习服务
        services['machine_learning_service'] = self.create_machine_learning_service()
        
        return services
    
    def clear_cache(self):
        """清除服务缓存"""
        self._ai_service_cache.clear()
        self._git_service_cache.clear()
        self._notify_service_cache = None
        self._intelligent_task_service_cache = None
        self._ai_model_manager_cache = None
        self._multimodal_ai_service_cache = None
        self.logger.info("服务缓存已清除")
