"""
智能任务生成服务 - 实现基于AI的智能任务生成和优化
"""

import json
import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from .ai_service import AIService


class TaskComplexity(Enum):
    """任务复杂度枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskType(Enum):
    """任务类型枚举"""
    CODING = "coding"
    REVIEW = "review"
    DOC = "doc"
    REQUIREMENT_REVIEW = "requirement_review"
    CUSTOM = "custom"


@dataclass
class TaskTemplate:
    """任务模板数据类"""
    template_id: str
    name: str
    description: str
    task_type: TaskType
    complexity: TaskComplexity
    estimated_duration: int  # 分钟
    success_rate: float  # 成功率 0-1
    avg_execution_time: int  # 平均执行时间（秒）
    parameters: Dict[str, Any]
    tags: List[str]
    usage_count: int
    last_used: Optional[datetime]
    created_at: datetime


@dataclass
class TaskPrediction:
    """任务预测结果"""
    estimated_duration: int  # 预估执行时间（分钟）
    success_probability: float  # 成功概率 0-1
    resource_requirements: Dict[str, Any]  # 资源需求
    complexity_score: float  # 复杂度评分 0-1
    risk_factors: List[str]  # 风险因素
    optimization_suggestions: List[str]  # 优化建议


class IntelligentTaskService:
    """智能任务生成服务"""
    
    def __init__(self, ai_service: AIService, config: Dict[str, Any]):
        """
        初始化智能任务生成服务
        
        Args:
            ai_service: AI服务实例
            config: 服务配置
        """
        self.ai_service = ai_service
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 任务模板库
        self.task_templates: Dict[str, TaskTemplate] = {}
        
        # 历史执行记录
        self.execution_history: List[Dict[str, Any]] = []
        
        # 参数优化规则
        self.optimization_rules = config.get('optimization_rules', {})
        
        # 初始化默认模板
        self._init_default_templates()
    
    def _init_default_templates(self):
        """初始化默认任务模板"""
        default_templates = [
            TaskTemplate(
                template_id="coding_basic",
                name="基础代码生成",
                description="生成基础功能代码",
                task_type=TaskType.CODING,
                complexity=TaskComplexity.LOW,
                estimated_duration=30,
                success_rate=0.85,
                avg_execution_time=1800,
                parameters={
                    "max_tokens": 4000,
                    "temperature": 0.1,
                    "model": "claude-3-sonnet-20240229"
                },
                tags=["基础功能", "代码生成"],
                usage_count=0,
                last_used=None,
                created_at=datetime.now()
            ),
            TaskTemplate(
                template_id="review_comprehensive",
                name="全面代码审查",
                description="进行全面的代码质量审查",
                task_type=TaskType.REVIEW,
                complexity=TaskComplexity.MEDIUM,
                estimated_duration=45,
                success_rate=0.90,
                avg_execution_time=2700,
                parameters={
                    "max_tokens": 3000,
                    "temperature": 0.1,
                    "model": "claude-3-sonnet-20240229"
                },
                tags=["代码审查", "质量检查"],
                usage_count=0,
                last_used=None,
                created_at=datetime.now()
            ),
            TaskTemplate(
                template_id="doc_api",
                name="API文档生成",
                description="生成API接口文档",
                task_type=TaskType.DOC,
                complexity=TaskComplexity.MEDIUM,
                estimated_duration=60,
                success_rate=0.88,
                avg_execution_time=3600,
                parameters={
                    "max_tokens": 5000,
                    "temperature": 0.1,
                    "model": "claude-3-sonnet-20240229"
                },
                tags=["API文档", "技术文档"],
                usage_count=0,
                last_used=None,
                created_at=datetime.now()
            )
        ]
        
        for template in default_templates:
            self.task_templates[template.template_id] = template
    
    def generate_task_from_natural_language(self, description: str, 
                                          context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        从自然语言描述生成任务配置
        
        Args:
            description: 自然语言任务描述
            context: 上下文信息
            
        Returns:
            生成的任务配置
        """
        try:
            self.logger.info(f"开始从自然语言生成任务: {description}")
            
            # 分析任务描述
            task_analysis = self._analyze_task_description(description, context)
            
            # 推荐任务模板
            recommended_templates = self._recommend_templates(task_analysis)
            
            # 生成任务配置
            task_config = self._generate_task_config(task_analysis, recommended_templates)
            
            # 优化参数
            optimized_config = self._optimize_parameters(task_config)
            
            # 预测执行效果
            prediction = self._predict_execution_effect(optimized_config)
            
            return {
                "task_config": optimized_config,
                "prediction": prediction,
                "recommended_templates": recommended_templates,
                "analysis": task_analysis
            }
            
        except Exception as e:
            self.logger.error(f"从自然语言生成任务失败: {e}")
            raise
    
    def _analyze_task_description(self, description: str, 
                                 context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        分析任务描述
        
        Args:
            description: 任务描述
            context: 上下文信息
            
        Returns:
            分析结果
        """
        try:
            # 构建分析提示词
            prompt = f"""
请分析以下任务描述，并返回JSON格式的分析结果：

任务描述：{description}

上下文信息：{context or '无'}

请分析以下方面：
1. 任务类型（coding/review/doc/requirement_review/custom）
2. 任务复杂度（low/medium/high）
3. 预估执行时间（分钟）
4. 关键功能点
5. 技术要求
6. 输出要求
7. 相关标签

返回格式：
{{
    "task_type": "任务类型",
    "complexity": "复杂度",
    "estimated_duration": 预估时间,
    "key_features": ["功能点1", "功能点2"],
    "technical_requirements": ["要求1", "要求2"],
    "output_requirements": ["输出1", "输出2"],
    "tags": ["标签1", "标签2"],
    "confidence_score": 0.85
}}
"""
            
            # 调用AI服务分析
            response = self.ai_service.execute_custom_task(prompt)
            
            # 解析分析结果
            analysis_result = self._parse_analysis_response(response)
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"分析任务描述失败: {e}")
            # 返回默认分析结果
            return {
                "task_type": "custom",
                "complexity": "medium",
                "estimated_duration": 30,
                "key_features": [],
                "technical_requirements": [],
                "output_requirements": [],
                "tags": [],
                "confidence_score": 0.5
            }
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """
        解析AI分析响应
        
        Args:
            response: AI响应内容
            
        Returns:
            解析后的分析结果
        """
        try:
            # 尝试提取JSON内容
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            else:
                # 如果无法解析JSON，使用正则表达式提取关键信息
                return self._extract_info_with_regex(response)
                
        except Exception as e:
            self.logger.warning(f"解析分析响应失败: {e}")
            return self._extract_info_with_regex(response)
    
    def _extract_info_with_regex(self, response: str) -> Dict[str, Any]:
        """
        使用正则表达式提取信息
        
        Args:
            response: AI响应内容
            
        Returns:
            提取的信息
        """
        result = {
            "task_type": "custom",
            "complexity": "medium",
            "estimated_duration": 30,
            "key_features": [],
            "technical_requirements": [],
            "output_requirements": [],
            "tags": [],
            "confidence_score": 0.5
        }
        
        # 提取任务类型
        if "coding" in response.lower() or "代码" in response:
            result["task_type"] = "coding"
        elif "review" in response.lower() or "审查" in response:
            result["task_type"] = "review"
        elif "doc" in response.lower() or "文档" in response:
            result["task_type"] = "doc"
        
        # 提取复杂度
        if "high" in response.lower() or "高" in response:
            result["complexity"] = "high"
        elif "low" in response.lower() or "低" in response:
            result["complexity"] = "low"
        
        # 提取预估时间
        time_match = re.search(r'(\d+)\s*分钟', response)
        if time_match:
            result["estimated_duration"] = int(time_match.group(1))
        
        return result
    
    def _recommend_templates(self, analysis: Dict[str, Any]) -> List[TaskTemplate]:
        """
        推荐任务模板
        
        Args:
            analysis: 任务分析结果
            
        Returns:
            推荐的模板列表
        """
        try:
            task_type = analysis.get("task_type", "custom")
            complexity = analysis.get("complexity", "medium")
            tags = analysis.get("tags", [])
            
            # 筛选匹配的模板
            matching_templates = []
            
            for template in self.task_templates.values():
                # 类型匹配
                if template.task_type.value != task_type:
                    continue
                
                # 复杂度匹配
                if template.complexity.value != complexity:
                    continue
                
                # 标签匹配度
                tag_similarity = self._calculate_tag_similarity(tags, template.tags)
                
                # 计算综合评分
                score = self._calculate_template_score(template, tag_similarity)
                
                matching_templates.append((template, score))
            
            # 按评分排序
            matching_templates.sort(key=lambda x: x[1], reverse=True)
            
            # 返回前3个推荐模板
            return [template for template, score in matching_templates[:3]]
            
        except Exception as e:
            self.logger.error(f"推荐模板失败: {e}")
            return []
    
    def _calculate_tag_similarity(self, user_tags: List[str], template_tags: List[str]) -> float:
        """
        计算标签相似度
        
        Args:
            user_tags: 用户标签
            template_tags: 模板标签
            
        Returns:
            相似度分数 0-1
        """
        if not user_tags or not template_tags:
            return 0.0
        
        # 计算交集大小
        intersection = set(user_tags) & set(template_tags)
        union = set(user_tags) | set(template_tags)
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
    
    def _calculate_template_score(self, template: TaskTemplate, tag_similarity: float) -> float:
        """
        计算模板评分
        
        Args:
            template: 任务模板
            tag_similarity: 标签相似度
            
        Returns:
            综合评分
        """
        # 成功率权重
        success_weight = 0.4
        # 使用次数权重
        usage_weight = 0.2
        # 标签相似度权重
        tag_weight = 0.3
        # 最近使用时间权重
        recency_weight = 0.1
        
        # 计算最近使用时间分数
        if template.last_used:
            days_since = (datetime.now() - template.last_used).days
            recency_score = max(0, 1 - days_since / 30)  # 30天内线性衰减
        else:
            recency_score = 0.5
        
        # 计算使用次数分数
        usage_score = min(1.0, template.usage_count / 10)  # 最多10次为满分
        
        # 综合评分
        score = (template.success_rate * success_weight +
                usage_score * usage_weight +
                tag_similarity * tag_weight +
                recency_score * recency_weight)
        
        return score
    
    def _generate_task_config(self, analysis: Dict[str, Any], 
                             templates: List[TaskTemplate]) -> Dict[str, Any]:
        """
        生成任务配置
        
        Args:
            analysis: 任务分析结果
            templates: 推荐模板
            
        Returns:
            任务配置
        """
        try:
            # 使用最佳匹配的模板作为基础
            base_template = templates[0] if templates else None
            
            # 生成任务ID
            task_id = f"auto_generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 构建基础配置
            config = {
                "task_id": task_id,
                "name": f"自动生成任务_{task_id}",
                "description": analysis.get("description", "自动生成的任务"),
                "type": analysis.get("task_type", "custom"),
                "enabled": True,
                "priority": 5,
                "schedule": {
                    "type": "manual"
                },
                "ai": {
                    "primary_model": "claude",
                    "model": "claude-3-sonnet-20240229",
                    "max_tokens": 4000,
                    "temperature": 0.1
                },
                "output": {
                    "format": "markdown",
                    "output_path": "./outputs/auto_generated"
                },
                "retry": {
                    "max_attempts": 3,
                    "base_delay": 30,
                    "max_delay": 300
                },
                "timeout": {
                    "task_timeout": 3600,
                    "ai_timeout": 1800
                }
            }
            
            # 根据模板优化配置
            if base_template:
                config["ai"].update(base_template.parameters)
                config["timeout"]["task_timeout"] = base_template.estimated_duration * 60
            
            # 根据任务类型添加特定配置
            task_type = analysis.get("task_type", "custom")
            if task_type == "coding":
                config["coding"] = {
                    "prompt": analysis.get("description", ""),
                    "language": "python",
                    "framework": "none"
                }
            elif task_type == "review":
                config["review"] = {
                    "prompt": analysis.get("description", ""),
                    "coding_standards": "default"
                }
            elif task_type == "doc":
                config["doc"] = {
                    "prompt": analysis.get("description", ""),
                    "doc_type": "markdown",
                    "output_format": "markdown"
                }
            
            return config
            
        except Exception as e:
            self.logger.error(f"生成任务配置失败: {e}")
            raise
    
    def _optimize_parameters(self, task_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        优化任务参数
        
        Args:
            task_config: 原始任务配置
            
        Returns:
            优化后的配置
        """
        try:
            optimized_config = task_config.copy()
            
            # 获取任务类型和复杂度
            task_type = task_config.get("type", "custom")
            complexity = self._estimate_complexity(task_config)
            
            # 应用优化规则
            optimization_rules = self.optimization_rules.get(task_type, {})
            
            # 优化AI参数
            ai_config = optimized_config.get("ai", {})
            if complexity == "high":
                ai_config["max_tokens"] = min(8000, ai_config.get("max_tokens", 4000) * 1.5)
                ai_config["temperature"] = max(0.05, ai_config.get("temperature", 0.1) * 0.8)
            elif complexity == "low":
                ai_config["max_tokens"] = max(2000, ai_config.get("max_tokens", 4000) * 0.7)
                ai_config["temperature"] = min(0.2, ai_config.get("temperature", 0.1) * 1.2)
            
            # 优化超时设置
            timeout_config = optimized_config.get("timeout", {})
            estimated_duration = self._estimate_duration(task_config)
            timeout_config["task_timeout"] = int(estimated_duration * 60 * 1.2)  # 增加20%缓冲
            timeout_config["ai_timeout"] = int(estimated_duration * 60 * 0.8)  # AI时间占80%
            
            # 优化重试策略
            retry_config = optimized_config.get("retry", {})
            if complexity == "high":
                retry_config["max_attempts"] = min(5, retry_config.get("max_attempts", 3) + 1)
                retry_config["base_delay"] = retry_config.get("base_delay", 30) * 1.5
            
            return optimized_config
            
        except Exception as e:
            self.logger.error(f"优化参数失败: {e}")
            return task_config
    
    def _estimate_complexity(self, task_config: Dict[str, Any]) -> str:
        """
        估算任务复杂度
        
        Args:
            task_config: 任务配置
            
        Returns:
            复杂度级别
        """
        try:
            # 基于多个因素估算复杂度
            factors = []
            
            # 任务类型复杂度
            type_complexity = {
                "coding": 0.6,
                "review": 0.4,
                "doc": 0.3,
                "requirement_review": 0.7,
                "custom": 0.5
            }
            factors.append(type_complexity.get(task_config.get("type", "custom"), 0.5))
            
            # 描述长度复杂度
            description = task_config.get("description", "")
            desc_length = len(description)
            if desc_length > 500:
                factors.append(0.8)
            elif desc_length > 200:
                factors.append(0.6)
            else:
                factors.append(0.4)
            
            # AI参数复杂度
            ai_config = task_config.get("ai", {})
            max_tokens = ai_config.get("max_tokens", 4000)
            if max_tokens > 6000:
                factors.append(0.8)
            elif max_tokens > 4000:
                factors.append(0.6)
            else:
                factors.append(0.4)
            
            # 计算平均复杂度
            avg_complexity = sum(factors) / len(factors)
            
            if avg_complexity > 0.7:
                return "high"
            elif avg_complexity > 0.4:
                return "medium"
            else:
                return "low"
                
        except Exception as e:
            self.logger.warning(f"估算复杂度失败: {e}")
            return "medium"
    
    def _estimate_duration(self, task_config: Dict[str, Any]) -> int:
        """
        估算任务执行时间（分钟）
        
        Args:
            task_config: 任务配置
            
        Returns:
            预估时间（分钟）
        """
        try:
            # 基础时间估算
            base_times = {
                "coding": 45,
                "review": 30,
                "doc": 60,
                "requirement_review": 90,
                "custom": 45
            }
            
            base_time = base_times.get(task_config.get("type", "custom"), 45)
            
            # 根据复杂度调整
            complexity = self._estimate_complexity(task_config)
            if complexity == "high":
                base_time *= 1.5
            elif complexity == "low":
                base_time *= 0.7
            
            # 根据描述长度调整
            description = task_config.get("description", "")
            desc_length = len(description)
            if desc_length > 500:
                base_time *= 1.3
            elif desc_length > 200:
                base_time *= 1.1
            
            return int(base_time)
            
        except Exception as e:
            self.logger.warning(f"估算执行时间失败: {e}")
            return 45
    
    def _predict_execution_effect(self, task_config: Dict[str, Any]) -> TaskPrediction:
        """
        预测任务执行效果
        
        Args:
            task_config: 任务配置
            
        Returns:
            预测结果
        """
        try:
            # 基于历史数据预测
            task_type = task_config.get("type", "custom")
            complexity = self._estimate_complexity(task_config)
            
            # 获取历史成功率
            historical_success_rate = self._get_historical_success_rate(task_type)
            
            # 获取历史执行时间
            historical_duration = self._get_historical_duration(task_type)
            
            # 计算预测值
            estimated_duration = self._estimate_duration(task_config)
            success_probability = historical_success_rate * 0.8 + 0.2  # 基础成功率
            
            # 根据复杂度调整
            if complexity == "high":
                success_probability *= 0.9
                estimated_duration *= 1.3
            elif complexity == "low":
                success_probability *= 1.1
                estimated_duration *= 0.8
            
            # 识别风险因素
            risk_factors = self._identify_risk_factors(task_config)
            
            # 生成优化建议
            optimization_suggestions = self._generate_optimization_suggestions(task_config, risk_factors)
            
            return TaskPrediction(
                estimated_duration=estimated_duration,
                success_probability=min(1.0, success_probability),
                resource_requirements={
                    "cpu": "medium",
                    "memory": "medium",
                    "disk": "low"
                },
                complexity_score=self._calculate_complexity_score(complexity),
                risk_factors=risk_factors,
                optimization_suggestions=optimization_suggestions
            )
            
        except Exception as e:
            self.logger.error(f"预测执行效果失败: {e}")
            return TaskPrediction(
                estimated_duration=45,
                success_probability=0.7,
                resource_requirements={},
                complexity_score=0.5,
                risk_factors=["预测失败"],
                optimization_suggestions=["无法生成优化建议"]
            )
    
    def _get_historical_success_rate(self, task_type: str) -> float:
        """
        获取历史成功率
        
        Args:
            task_type: 任务类型
            
        Returns:
            历史成功率
        """
        try:
            if not self.execution_history:
                return 0.8  # 默认成功率
            
            # 筛选同类型任务
            type_history = [h for h in self.execution_history if h.get("task_type") == task_type]
            
            if not type_history:
                return 0.8
            
            # 计算成功率
            successful = sum(1 for h in type_history if h.get("status") == "success")
            return successful / len(type_history)
            
        except Exception as e:
            self.logger.warning(f"获取历史成功率失败: {e}")
            return 0.8
    
    def _get_historical_duration(self, task_type: str) -> int:
        """
        获取历史执行时间
        
        Args:
            task_type: 任务类型
            
        Returns:
            平均执行时间（分钟）
        """
        try:
            if not self.execution_history:
                return 45
            
            # 筛选同类型任务
            type_history = [h for h in self.execution_history if h.get("task_type") == task_type]
            
            if not type_history:
                return 45
            
            # 计算平均时间
            durations = [h.get("duration", 45) for h in type_history]
            return int(sum(durations) / len(durations))
            
        except Exception as e:
            self.logger.warning(f"获取历史执行时间失败: {e}")
            return 45
    
    def _identify_risk_factors(self, task_config: Dict[str, Any]) -> List[str]:
        """
        识别风险因素
        
        Args:
            task_config: 任务配置
            
        Returns:
            风险因素列表
        """
        risk_factors = []
        
        try:
            # 检查描述长度
            description = task_config.get("description", "")
            if len(description) > 1000:
                risk_factors.append("任务描述过长，可能导致理解偏差")
            
            # 检查AI参数
            ai_config = task_config.get("ai", {})
            if ai_config.get("max_tokens", 4000) > 8000:
                risk_factors.append("Token限制过高，可能影响响应质量")
            
            # 检查超时设置
            timeout_config = task_config.get("timeout", {})
            if timeout_config.get("task_timeout", 3600) < 1800:
                risk_factors.append("任务超时时间过短")
            
            # 检查任务类型
            task_type = task_config.get("type", "custom")
            if task_type == "custom":
                risk_factors.append("自定义任务类型，执行效果不确定")
            
            return risk_factors
            
        except Exception as e:
            self.logger.warning(f"识别风险因素失败: {e}")
            return ["风险评估失败"]
    
    def _generate_optimization_suggestions(self, task_config: Dict[str, Any], 
                                         risk_factors: List[str]) -> List[str]:
        """
        生成优化建议
        
        Args:
            task_config: 任务配置
            risk_factors: 风险因素
            
        Returns:
            优化建议列表
        """
        suggestions = []
        
        try:
            # 基于风险因素生成建议
            for risk in risk_factors:
                if "描述过长" in risk:
                    suggestions.append("建议将任务描述控制在500字以内")
                elif "Token限制过高" in risk:
                    suggestions.append("建议将max_tokens设置为4000-6000")
                elif "超时时间过短" in risk:
                    suggestions.append("建议将任务超时时间设置为至少30分钟")
                elif "自定义任务" in risk:
                    suggestions.append("建议使用标准任务类型以提高成功率")
            
            # 基于任务类型生成建议
            task_type = task_config.get("type", "custom")
            if task_type == "coding":
                suggestions.append("建议指定编程语言和框架")
            elif task_type == "review":
                suggestions.append("建议提供具体的编码规范")
            elif task_type == "doc":
                suggestions.append("建议指定文档类型和输出格式")
            
            # 基于复杂度生成建议
            complexity = self._estimate_complexity(task_config)
            if complexity == "high":
                suggestions.append("建议将复杂任务拆分为多个子任务")
                suggestions.append("建议增加重试次数和超时时间")
            
            return suggestions
            
        except Exception as e:
            self.logger.warning(f"生成优化建议失败: {e}")
            return ["无法生成优化建议"]
    
    def _calculate_complexity_score(self, complexity: str) -> float:
        """
        计算复杂度评分
        
        Args:
            complexity: 复杂度级别
            
        Returns:
            复杂度评分 0-1
        """
        complexity_scores = {
            "low": 0.3,
            "medium": 0.6,
            "high": 0.9
        }
        return complexity_scores.get(complexity, 0.6)
    
    def add_execution_record(self, task_id: str, task_config: Dict[str, Any], 
                           execution_result: Dict[str, Any]):
        """
        添加执行记录
        
        Args:
            task_id: 任务ID
            task_config: 任务配置
            execution_result: 执行结果
        """
        try:
            record = {
                "task_id": task_id,
                "task_type": task_config.get("type", "custom"),
                "status": execution_result.get("status", "unknown"),
                "duration": execution_result.get("duration", 0),
                "success": execution_result.get("success", False),
                "error_message": execution_result.get("error_message", ""),
                "execution_time": datetime.now().isoformat()
            }
            
            self.execution_history.append(record)
            
            # 更新模板使用统计
            self._update_template_usage(task_config)
            
            # 限制历史记录数量
            if len(self.execution_history) > 1000:
                self.execution_history = self.execution_history[-500:]
                
        except Exception as e:
            self.logger.error(f"添加执行记录失败: {e}")
    
    def _update_template_usage(self, task_config: Dict[str, Any]):
        """
        更新模板使用统计
        
        Args:
            task_config: 任务配置
        """
        try:
            # 找到最匹配的模板
            task_type = task_config.get("type", "custom")
            complexity = self._estimate_complexity(task_config)
            
            for template in self.task_templates.values():
                if (template.task_type.value == task_type and 
                    template.complexity.value == complexity):
                    template.usage_count += 1
                    template.last_used = datetime.now()
                    break
                    
        except Exception as e:
            self.logger.warning(f"更新模板使用统计失败: {e}")
    
    def get_task_templates(self, task_type: Optional[str] = None, 
                          complexity: Optional[str] = None) -> List[TaskTemplate]:
        """
        获取任务模板
        
        Args:
            task_type: 任务类型过滤
            complexity: 复杂度过滤
            
        Returns:
            模板列表
        """
        try:
            templates = list(self.task_templates.values())
            
            # 应用过滤条件
            if task_type:
                templates = [t for t in templates if t.task_type.value == task_type]
            
            if complexity:
                templates = [t for t in templates if t.complexity.value == complexity]
            
            # 按使用次数排序
            templates.sort(key=lambda t: t.usage_count, reverse=True)
            
            return templates
            
        except Exception as e:
            self.logger.error(f"获取任务模板失败: {e}")
            return []
    
    def add_task_template(self, template: TaskTemplate):
        """
        添加任务模板
        
        Args:
            template: 任务模板
        """
        try:
            self.task_templates[template.template_id] = template
            self.logger.info(f"添加任务模板: {template.template_id}")
            
        except Exception as e:
            self.logger.error(f"添加任务模板失败: {e}")
            raise
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """
        获取执行统计信息
        
        Returns:
            统计信息
        """
        try:
            if not self.execution_history:
                return {
                    "total_executions": 0,
                    "success_rate": 0.0,
                    "avg_duration": 0,
                    "task_type_distribution": {},
                    "recent_executions": []
                }
            
            # 计算基础统计
            total_executions = len(self.execution_history)
            successful_executions = sum(1 for h in self.execution_history if h.get("success", False))
            success_rate = successful_executions / total_executions if total_executions > 0 else 0.0
            
            # 计算平均执行时间
            durations = [h.get("duration", 0) for h in self.execution_history]
            avg_duration = sum(durations) / len(durations) if durations else 0
            
            # 任务类型分布
            task_type_distribution = {}
            for record in self.execution_history:
                task_type = record.get("task_type", "unknown")
                task_type_distribution[task_type] = task_type_distribution.get(task_type, 0) + 1
            
            # 最近执行记录
            recent_executions = sorted(
                self.execution_history, 
                key=lambda x: x.get("execution_time", ""), 
                reverse=True
            )[:10]
            
            return {
                "total_executions": total_executions,
                "success_rate": success_rate,
                "avg_duration": avg_duration,
                "task_type_distribution": task_type_distribution,
                "recent_executions": recent_executions
            }
            
        except Exception as e:
            self.logger.error(f"获取执行统计失败: {e}")
            return {
                "total_executions": 0,
                "success_rate": 0.0,
                "avg_duration": 0,
                "task_type_distribution": {},
                "recent_executions": []
            }
