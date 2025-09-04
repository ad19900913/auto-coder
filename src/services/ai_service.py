"""
AI服务模块 - 支持多种AI模型的统一接口
"""

import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import requests


class AIService(ABC):
    """AI服务抽象基类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化AI服务
        
        Args:
            config: AI服务配置
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.api_key = config.get('api_key', '')
        self.base_url = config.get('base_url', '')
        self.model = config.get('model', '')
        
        if not self.api_key:
            raise ValueError("API密钥不能为空")
    
    @abstractmethod
    def generate_code(self, prompt: str, task_type: str = "coding", **kwargs) -> str:
        """
        生成代码
        
        Args:
            prompt: 提示词
            task_type: 任务类型
            **kwargs: 其他参数
            
        Returns:
            生成的代码
        """
        pass
    
    @abstractmethod
    def review_code(self, code: str, coding_standards: str, **kwargs) -> Dict[str, Any]:
        """
        审查代码
        
        Args:
            code: 要审查的代码
            coding_standards: 编码规范
            **kwargs: 其他参数
            
        Returns:
            审查结果
        """
        pass
    
    @abstractmethod
    def analyze_requirement_code(self, requirement: str, code: str, **kwargs) -> Dict[str, Any]:
        """
        分析需求与代码的一致性
        
        Args:
            requirement: 需求文档
            code: 代码实现
            **kwargs: 其他参数
            
        Returns:
            分析结果
        """
        pass
    
    @abstractmethod
    def execute_custom_task(self, prompt: str, **kwargs) -> str:
        """
        执行自定义任务
        
        Args:
            prompt: 任务提示词
            **kwargs: 其他参数
            
        Returns:
            任务执行结果
        """
        pass


class ClaudeService(AIService):
    """Claude AI服务实现"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key,
            'anthropic-version': '2023-06-01'
        }
    
    def generate_code(self, prompt: str, task_type: str = "coding", **kwargs) -> str:
        """生成代码"""
        try:
            # 构建系统提示词
            system_prompt = self._build_system_prompt(task_type)
            
            # 构建用户提示词
            user_prompt = f"{system_prompt}\n\n{prompt}"
            
            # 调用Claude API
            response = self._call_claude_api(user_prompt, task_type, **kwargs)
            
            return response
            
        except Exception as e:
            self.logger.error(f"代码生成失败: {e}")
            raise
    
    def review_code(self, code: str, coding_standards: str, **kwargs) -> Dict[str, Any]:
        """审查代码"""
        try:
            system_prompt = self._build_review_prompt(coding_standards)
            user_prompt = f"请审查以下代码，并按照编码规范指出问题：\n\n```\n{code}\n```"
            
            response = self._call_claude_api(user_prompt, "review", **kwargs)
            
            # 解析审查结果
            review_result = self._parse_review_response(response)
            
            return review_result
            
        except Exception as e:
            self.logger.error(f"代码审查失败: {e}")
            raise
    
    def analyze_requirement_code(self, requirement: str, code: str, **kwargs) -> Dict[str, Any]:
        """分析需求与代码的一致性"""
        try:
            system_prompt = self._build_requirement_analysis_prompt()
            user_prompt = f"""
需求文档：
{requirement}

代码实现：
{code}

请分析需求与代码实现的一致性，指出：
1. 功能实现是否完整
2. 架构设计是否合理
3. 接口定义是否一致
4. 数据模型是否匹配
5. 发现的问题和建议
"""
            
            response = self._call_claude_api(user_prompt, "requirement_review", **kwargs)
            
            # 解析分析结果
            analysis_result = self._parse_analysis_response(response)
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"需求代码分析失败: {e}")
            raise
    
    def execute_custom_task(self, prompt: str, **kwargs) -> str:
        """执行自定义任务"""
        try:
            system_prompt = "你是一个专业的AI助手，请根据用户的要求完成任务。"
            user_prompt = f"任务要求：{prompt}"
            
            response = self._call_claude_api(user_prompt, "custom", **kwargs)
            
            return response
            
        except Exception as e:
            self.logger.error(f"自定义任务执行失败: {e}")
            raise
    
    def _call_claude_api(self, prompt: str, task_type: str, **kwargs) -> str:
        """调用Claude API"""
        try:
            # 获取任务特定参数
            task_params = self.config.get('task_parameters', {}).get(task_type, {})
            
            # 构建请求参数
            request_data = {
                'model': self.model,
                'max_tokens': task_params.get('max_tokens', 4000),
                'temperature': task_params.get('temperature', 0.1),
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            }
            
            # 发送请求
            response = requests.post(
                f"{self.base_url}/v1/messages",
                headers=self.headers,
                json=request_data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['content'][0]['text']
                return content
            else:
                error_msg = f"Claude API调用失败: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            self.logger.error(f"Claude API调用异常: {e}")
            raise
    
    def _build_system_prompt(self, task_type: str) -> str:
        """构建系统提示词"""
        if task_type == "coding":
            return """你是一个专业的代码生成助手。请根据用户的需求生成高质量的代码。

要求：
1. 代码要符合最佳实践和设计模式
2. 包含必要的注释和文档
3. 考虑错误处理和边界情况
4. 遵循SOLID原则
5. 代码要易于理解和维护

请生成完整的代码实现。"""
        
        elif task_type == "review":
            return """你是一个专业的代码审查助手。请仔细审查代码，指出问题并提供改进建议。

审查要点：
1. 代码质量和规范性
2. 性能和安全问题
3. 设计模式和架构
4. 错误处理
5. 测试覆盖

请提供详细的审查报告。"""
        
        else:
            return "你是一个专业的AI助手，请根据用户的要求完成任务。"
    
    def _build_review_prompt(self, coding_standards: str) -> str:
        """构建代码审查提示词"""
        return f"""你是一个专业的代码审查助手。请根据以下编码规范审查代码：

编码规范：
{coding_standards}

审查要求：
1. 检查代码是否符合编码规范
2. 指出代码质量问题
3. 提供具体的改进建议
4. 评估代码的可维护性

请提供结构化的审查报告。"""
    
    def _build_requirement_analysis_prompt(self) -> str:
        """构建需求分析提示词"""
        return """你是一个专业的需求分析师和架构师。请分析需求文档与代码实现的一致性。

分析维度：
1. 功能完整性：代码是否实现了所有需求功能
2. 架构合理性：代码架构是否满足需求要求
3. 接口一致性：API设计是否与需求描述一致
4. 数据模型：数据结构是否支持需求场景
5. 非功能性需求：性能、安全、可扩展性等

请提供详细的分析报告。"""
    
    def _parse_review_response(self, response: str) -> Dict[str, Any]:
        """解析代码审查响应"""
        try:
            # 简单的解析逻辑，实际项目中可以使用更复杂的解析
            issues = []
            suggestions = []
            
            lines = response.split('\n')
            for line in lines:
                if '问题' in line or 'issue' in line.lower():
                    issues.append(line.strip())
                elif '建议' in line or 'suggestion' in line.lower():
                    suggestions.append(line.strip())
            
            return {
                'issues': issues,
                'suggestions': suggestions,
                'issues_count': len(issues),
                'raw_response': response
            }
            
        except Exception as e:
            self.logger.warning(f"解析审查响应失败: {e}")
            return {
                'issues': [],
                'suggestions': [],
                'issues_count': 0,
                'raw_response': response
            }
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """解析需求分析响应"""
        try:
            # 简单的解析逻辑
            inconsistencies = []
            recommendations = []
            
            lines = response.split('\n')
            for line in lines:
                if '不一致' in line or 'inconsistency' in line.lower():
                    inconsistencies.append(line.strip())
                elif '建议' in line or 'recommendation' in line.lower():
                    recommendations.append(line.strip())
            
            return {
                'inconsistencies': inconsistencies,
                'recommendations': recommendations,
                'inconsistencies_count': len(inconsistencies),
                'raw_response': response
            }
            
        except Exception as e:
            self.logger.warning(f"解析分析响应失败: {e}")
            return {
                'inconsistencies': [],
                'recommendations': [],
                'inconsistencies_count': 0,
                'raw_response': response
            }


class DeepSeekService(AIService):
    """DeepSeek AI服务实现"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
    
    def generate_code(self, prompt: str, task_type: str = "coding", **kwargs) -> str:
        """生成代码"""
        try:
            system_prompt = self._build_system_prompt(task_type)
            user_prompt = f"{system_prompt}\n\n{prompt}"
            
            response = self._call_deepseek_api(user_prompt, task_type, **kwargs)
            return response
            
        except Exception as e:
            self.logger.error(f"代码生成失败: {e}")
            raise
    
    def review_code(self, code: str, coding_standards: str, **kwargs) -> Dict[str, Any]:
        """审查代码"""
        try:
            system_prompt = self._build_review_prompt(coding_standards)
            user_prompt = f"请审查以下代码，并按照编码规范指出问题：\n\n```\n{code}\n```"
            
            response = self._call_deepseek_api(user_prompt, "review", **kwargs)
            review_result = self._parse_review_response(response)
            
            return review_result
            
        except Exception as e:
            self.logger.error(f"代码审查失败: {e}")
            raise
    
    def analyze_requirement_code(self, requirement: str, code: str, **kwargs) -> Dict[str, Any]:
        """分析需求与代码的一致性"""
        try:
            system_prompt = self._build_requirement_analysis_prompt()
            user_prompt = f"""
需求文档：
{requirement}

代码实现：
{code}

请分析需求与代码实现的一致性。
"""
            
            response = self._call_deepseek_api(user_prompt, "requirement_review", **kwargs)
            analysis_result = self._parse_analysis_response(response)
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"需求代码分析失败: {e}")
            raise
    
    def execute_custom_task(self, prompt: str, **kwargs) -> str:
        """执行自定义任务"""
        try:
            system_prompt = "你是一个专业的AI助手，请根据用户的要求完成任务。"
            user_prompt = f"任务要求：{prompt}"
            
            response = self._call_deepseek_api(user_prompt, "custom", **kwargs)
            return response
            
        except Exception as e:
            self.logger.error(f"自定义任务执行失败: {e}")
            raise
    
    def _call_deepseek_api(self, prompt: str, task_type: str, **kwargs) -> str:
        """调用DeepSeek API"""
        try:
            # 获取任务特定参数
            task_params = self.config.get('task_parameters', {}).get(task_type, {})
            
            # 构建请求参数
            request_data = {
                'model': self.model,
                'messages': [
                    {'role': 'system', 'content': '你是一个专业的AI助手。'},
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': task_params.get('max_tokens', 4000),
                'temperature': task_params.get('temperature', 0.1)
            }
            
            # 发送请求
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers=self.headers,
                json=request_data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                return content
            else:
                error_msg = f"DeepSeek API调用失败: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            self.logger.error(f"DeepSeek API调用异常: {e}")
            raise
    
    def _build_system_prompt(self, task_type: str) -> str:
        """构建系统提示词（与Claude类似）"""
        if task_type == "coding":
            return """你是一个专业的代码生成助手。请根据用户的需求生成高质量的代码。

要求：
1. 代码要符合最佳实践和设计模式
2. 包含必要的注释和文档
3. 考虑错误处理和边界情况
4. 遵循SOLID原则
5. 代码要易于理解和维护

请生成完整的代码实现。"""
        
        elif task_type == "review":
            return """你是一个专业的代码审查助手。请仔细审查代码，指出问题并提供改进建议。

审查要点：
1. 代码质量和规范性
2. 性能和安全问题
3. 设计模式和架构
4. 错误处理
5. 测试覆盖

请提供详细的审查报告。"""
        
        else:
            return "你是一个专业的AI助手，请根据用户的要求完成任务。"
    
    def _build_review_prompt(self, coding_standards: str) -> str:
        """构建代码审查提示词"""
        return f"""你是一个专业的代码审查助手。请根据以下编码规范审查代码：

编码规范：
{coding_standards}

审查要求：
1. 检查代码是否符合编码规范
2. 指出代码质量问题
3. 提供具体的改进建议
4. 评估代码的可维护性

请提供结构化的审查报告。"""
    
    def _build_requirement_analysis_prompt(self) -> str:
        """构建需求分析提示词"""
        return """你是一个专业的需求分析师和架构师。请分析需求文档与代码实现的一致性。

分析维度：
1. 功能完整性：代码是否实现了所有需求功能
2. 架构合理性：代码架构是否满足需求要求
3. 接口一致性：API设计是否与需求描述一致
4. 数据模型：数据结构是否支持需求场景
5. 非功能性需求：性能、安全、可扩展性等

请提供详细的分析报告。"""
    
    def _parse_review_response(self, response: str) -> Dict[str, Any]:
        """解析代码审查响应（与Claude类似）"""
        try:
            issues = []
            suggestions = []
            
            lines = response.split('\n')
            for line in lines:
                if '问题' in line or 'issue' in line.lower():
                    issues.append(line.strip())
                elif '建议' in line or 'suggestion' in line.lower():
                    suggestions.append(line.strip())
            
            return {
                'issues': issues,
                'suggestions': suggestions,
                'issues_count': len(issues),
                'raw_response': response
            }
            
        except Exception as e:
            self.logger.warning(f"解析审查响应失败: {e}")
            return {
                'issues': [],
                'suggestions': [],
                'issues_count': 0,
                'raw_response': response
            }
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """解析需求分析响应（与Claude类似）"""
        try:
            inconsistencies = []
            recommendations = []
            
            lines = response.split('\n')
            for line in lines:
                if '不一致' in line or 'inconsistency' in line.lower():
                    inconsistencies.append(line.strip())
                elif '建议' in line or 'recommendation' in line.lower():
                    recommendations.append(line.strip())
            
            return {
                'inconsistencies': inconsistencies,
                'recommendations': recommendations,
                'inconsistencies_count': len(inconsistencies),
                'raw_response': response
            }
            
        except Exception as e:
            self.logger.warning(f"解析分析响应失败: {e}")
            return {
                'inconsistencies': [],
                'recommendations': [],
                'inconsistencies_count': 0,
                'raw_response': response
            }


class GeminiService(AIService):
    """Gemini AI服务实现"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # 配置Gemini API
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
    
    def generate_code(self, prompt: str, task_type: str = "coding", **kwargs) -> str:
        """生成代码"""
        try:
            system_prompt = self._build_system_prompt(task_type)
            user_prompt = f"{system_prompt}\n\n{prompt}"
            
            response = self._call_gemini_api(user_prompt, task_type, **kwargs)
            return response
            
        except Exception as e:
            self.logger.error(f"代码生成失败: {e}")
            raise
    
    def review_code(self, code: str, coding_standards: str, **kwargs) -> Dict[str, Any]:
        """审查代码"""
        try:
            system_prompt = self._build_review_prompt(coding_standards)
            user_prompt = f"请审查以下代码，并按照编码规范指出问题：\n\n```\n{code}\n```"
            
            response = self._call_gemini_api(user_prompt, "review", **kwargs)
            review_result = self._parse_review_response(response)
            
            return review_result
            
        except Exception as e:
            self.logger.error(f"代码审查失败: {e}")
            raise
    
    def analyze_requirement_code(self, requirement: str, code: str, **kwargs) -> Dict[str, Any]:
        """分析需求与代码的一致性"""
        try:
            system_prompt = self._build_requirement_analysis_prompt()
            user_prompt = f"""
需求文档：
{requirement}

代码实现：
{code}

请分析需求与代码实现的一致性。
"""
            
            response = self._call_gemini_api(user_prompt, "requirement_review", **kwargs)
            analysis_result = self._parse_analysis_response(response)
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"需求代码分析失败: {e}")
            raise
    
    def execute_custom_task(self, prompt: str, **kwargs) -> str:
        """执行自定义任务"""
        try:
            system_prompt = "你是一个专业的AI助手，请根据用户的要求完成任务。"
            user_prompt = f"任务要求：{prompt}"
            
            response = self._call_gemini_api(user_prompt, "custom", **kwargs)
            return response
            
        except Exception as e:
            self.logger.error(f"自定义任务执行失败: {e}")
            raise
    
    def _call_gemini_api(self, prompt: str, task_type: str, **kwargs) -> str:
        """调用Gemini API"""
        try:
            # 获取任务特定参数
            task_params = self.config.get('task_parameters', {}).get(task_type, {})
            
            # 构建请求参数
            request_data = {
                'contents': [{
                    'parts': [{
                        'text': prompt
                    }]
                }],
                'generationConfig': {
                    'temperature': task_params.get('temperature', 0.1),
                    'topP': task_params.get('top_p', 0.8),
                    'topK': task_params.get('top_k', 40),
                    'maxOutputTokens': task_params.get('max_tokens', 4000),
                }
            }
            
            # 发送请求
            url = f"{self.base_url}/v1/models/{self.model}:generateContent"
            response = requests.post(
                url,
                headers=self.headers,
                json=request_data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    content = result['candidates'][0]['content']
                    if 'parts' in content and len(content['parts']) > 0:
                        return content['parts'][0]['text']
                    else:
                        raise Exception("Gemini API返回的内容格式不正确")
                else:
                    raise Exception("Gemini API返回空响应")
            else:
                raise Exception(f"Gemini API调用失败: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.logger.error(f"Gemini API调用失败: {e}")
            raise
    
    def _build_system_prompt(self, task_type: str) -> str:
        """构建系统提示词（与DeepSeek类似）"""
        if task_type == "coding":
            return """你是一个专业的代码生成助手。请根据用户的需求生成高质量的代码。

代码生成要求：
1. 代码结构清晰，注释完整
2. 遵循最佳实践和设计模式
3. 考虑错误处理和边界情况
4. 提供必要的文档说明
5. 确保代码可维护和可扩展

请生成完整的代码实现。"""
        
        elif task_type == "review":
            return """你是一个专业的代码审查助手。请仔细审查代码，指出问题并提供改进建议。

审查要点：
1. 代码质量和规范性
2. 性能和安全问题
3. 设计模式和架构
4. 错误处理
5. 测试覆盖

请提供详细的审查报告。"""
        
        else:
            return "你是一个专业的AI助手，请根据用户的要求完成任务。"
    
    def _build_review_prompt(self, coding_standards: str) -> str:
        """构建代码审查提示词（与DeepSeek类似）"""
        return f"""你是一个专业的代码审查助手。请根据以下编码规范审查代码：

编码规范：
{coding_standards}

审查要求：
1. 检查代码是否符合编码规范
2. 指出代码质量问题
3. 提供具体的改进建议
4. 评估代码的可维护性

请提供结构化的审查报告。"""
    
    def _build_requirement_analysis_prompt(self) -> str:
        """构建需求分析提示词（与DeepSeek类似）"""
        return """你是一个专业的需求分析师和架构师。请分析需求文档与代码实现的一致性。

分析维度：
1. 功能完整性：代码是否实现了所有需求功能
2. 架构合理性：代码架构是否满足需求要求
3. 接口一致性：API设计是否与需求描述一致
4. 数据模型：数据结构是否支持需求场景
5. 非功能性需求：性能、安全、可扩展性等

请提供详细的分析报告。"""


class CursorService(AIService):
    """Cursor AI服务实现"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # 配置Cursor API
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
    
    def generate_code(self, prompt: str, task_type: str = "coding", **kwargs) -> str:
        """生成代码"""
        try:
            system_prompt = self._build_system_prompt(task_type)
            user_prompt = f"{system_prompt}\n\n{prompt}"
            
            response = self._call_cursor_api(user_prompt, task_type, **kwargs)
            return response
            
        except Exception as e:
            self.logger.error(f"代码生成失败: {e}")
            raise
    
    def review_code(self, code: str, coding_standards: str, **kwargs) -> Dict[str, Any]:
        """审查代码"""
        try:
            system_prompt = self._build_review_prompt(coding_standards)
            user_prompt = f"请审查以下代码，并按照编码规范指出问题：\n\n```\n{code}\n```"
            
            response = self._call_cursor_api(user_prompt, "review", **kwargs)
            review_result = self._parse_review_response(response)
            
            return review_result
            
        except Exception as e:
            self.logger.error(f"代码审查失败: {e}")
            raise
    
    def analyze_requirement_code(self, requirement: str, code: str, **kwargs) -> Dict[str, Any]:
        """分析需求与代码的一致性"""
        try:
            system_prompt = self._build_requirement_analysis_prompt()
            user_prompt = f"""
需求文档：
{requirement}

代码实现：
{code}

请分析需求与代码实现的一致性。
"""
            
            response = self._call_cursor_api(user_prompt, "requirement_review", **kwargs)
            analysis_result = self._parse_analysis_response(response)
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"需求代码分析失败: {e}")
            raise
    
    def execute_custom_task(self, prompt: str, **kwargs) -> str:
        """执行自定义任务"""
        try:
            system_prompt = "你是一个专业的AI助手，请根据用户的要求完成任务。"
            user_prompt = f"任务要求：{prompt}"
            
            response = self._call_cursor_api(user_prompt, "custom", **kwargs)
            return response
            
        except Exception as e:
            self.logger.error(f"自定义任务执行失败: {e}")
            raise
    
    def _call_cursor_api(self, prompt: str, task_type: str, **kwargs) -> str:
        """调用Cursor API"""
        try:
            # 获取任务特定参数
            task_params = self.config.get('task_parameters', {}).get(task_type, {})
            
            # 构建请求参数
            request_data = {
                'model': self.model,
                'messages': [
                    {'role': 'system', 'content': '你是一个专业的AI助手。'},
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': task_params.get('max_tokens', 4000),
                'temperature': task_params.get('temperature', 0.1),
                'stream': False
            }
            
            # 发送请求
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers=self.headers,
                json=request_data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                return content
            else:
                raise Exception(f"Cursor API调用失败: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.logger.error(f"Cursor API调用失败: {e}")
            raise
    
    def _build_system_prompt(self, task_type: str) -> str:
        """构建系统提示词（与DeepSeek类似）"""
        if task_type == "coding":
            return """你是一个专业的代码生成助手。请根据用户的需求生成高质量的代码。

代码生成要求：
1. 代码结构清晰，注释完整
2. 遵循最佳实践和设计模式
3. 考虑错误处理和边界情况
4. 提供必要的文档说明
5. 确保代码可维护和可扩展

请生成完整的代码实现。"""
        
        elif task_type == "review":
            return """你是一个专业的代码审查助手。请仔细审查代码，指出问题并提供改进建议。

审查要点：
1. 代码质量和规范性
2. 性能和安全问题
3. 设计模式和架构
4. 错误处理
5. 测试覆盖

请提供详细的审查报告。"""
        
        else:
            return "你是一个专业的AI助手，请根据用户的要求完成任务。"
    
    def _build_review_prompt(self, coding_standards: str) -> str:
        """构建代码审查提示词（与DeepSeek类似）"""
        return f"""你是一个专业的代码审查助手。请根据以下编码规范审查代码：

编码规范：
{coding_standards}

审查要求：
1. 检查代码是否符合编码规范
2. 指出代码质量问题
3. 提供具体的改进建议
4. 评估代码的可维护性

请提供结构化的审查报告。"""
    
    def _build_requirement_analysis_prompt(self) -> str:
        """构建需求分析提示词（与DeepSeek类似）"""
        return """你是一个专业的需求分析师和架构师。请分析需求文档与代码实现的一致性。

分析维度：
1. 功能完整性：代码是否实现了所有需求功能
2. 架构合理性：代码架构是否满足需求要求
3. 接口一致性：API设计是否与需求描述一致
4. 数据模型：数据结构是否支持需求场景
5. 非功能性需求：性能、安全、可扩展性等

请提供详细的分析报告。"""
