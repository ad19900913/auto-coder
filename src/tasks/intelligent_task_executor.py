"""
智能任务生成任务执行器 - 实现基于AI的智能任务生成和优化
"""

import logging
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from ..core.task_executor import TaskExecutor


class IntelligentTaskExecutor(TaskExecutor):
    """智能任务生成任务执行器，负责基于AI的智能任务生成和优化"""
    
    def _execute_task(self) -> Dict[str, Any]:
        """
        执行智能任务生成任务
        
        Returns:
            执行结果字典
        """
        try:
            self.logger.info(f"开始执行智能任务生成任务: {self.task_id}")
            
            # 更新进度
            self._update_progress(10, "初始化智能任务生成任务")
            
            # 获取任务配置
            intelligent_task_config = self.task_config.get('intelligent_task', {})
            natural_language_description = intelligent_task_config.get('description')
            context = intelligent_task_config.get('context', {})
            
            if not natural_language_description:
                raise ValueError("智能任务生成任务配置不完整，缺少description")
            
            # 更新进度
            self._update_progress(20, "分析自然语言描述")
            
            # 从自然语言生成任务
            generation_result = self.intelligent_task_service.generate_task_from_natural_language(
                natural_language_description, context
            )
            
            # 更新进度
            self._update_progress(50, "生成任务配置")
            
            # 获取生成的任务配置
            task_config = generation_result['task_config']
            prediction = generation_result['prediction']
            recommended_templates = generation_result['recommended_templates']
            analysis = generation_result['analysis']
            
            # 更新进度
            self._update_progress(70, "保存生成结果")
            
            # 保存生成的任务配置
            output_path = self._save_generated_task(task_config, prediction, analysis)
            
            # 更新进度
            self._update_progress(90, "生成报告")
            
            # 生成执行报告
            report = self._generate_execution_report(
                task_config, prediction, recommended_templates, analysis, output_path
            )
            
            # 更新进度
            self._update_progress(100, "任务完成")
            
            return {
                "status": "success",
                "generated_task_config": task_config,
                "prediction": prediction,
                "recommended_templates": recommended_templates,
                "analysis": analysis,
                "output_path": output_path,
                "report": report,
                "message": "智能任务生成成功"
            }
            
        except Exception as e:
            self.logger.error(f"智能任务生成任务执行失败: {e}")
            return {
                "status": "error",
                "error_message": str(e),
                "message": "智能任务生成失败"
            }
    
    def _save_generated_task(self, task_config: Dict[str, Any], 
                           prediction: Any, analysis: Dict[str, Any]) -> str:
        """
        保存生成的任务配置
        
        Args:
            task_config: 生成的任务配置
            prediction: 预测结果
            analysis: 分析结果
            
        Returns:
            输出文件路径
        """
        try:
            # 获取输出配置
            output_config = self.task_config.get('output', {})
            output_path = output_config.get('output_path', './outputs/intelligent_tasks')
            filename_template = output_config.get('filename_template', 'generated_task_{timestamp}')
            
            # 创建输出目录
            os.makedirs(output_path, exist_ok=True)
            
            # 生成文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = filename_template.replace('{timestamp}', timestamp)
            
            # 构建完整的输出内容
            output_content = {
                "generated_at": datetime.now().isoformat(),
                "original_description": self.task_config.get('intelligent_task', {}).get('description'),
                "task_config": task_config,
                "prediction": {
                    "estimated_duration": prediction.estimated_duration,
                    "success_probability": prediction.success_probability,
                    "resource_requirements": prediction.resource_requirements,
                    "complexity_score": prediction.complexity_score,
                    "risk_factors": prediction.risk_factors,
                    "optimization_suggestions": prediction.optimization_suggestions
                },
                "analysis": analysis,
                "metadata": {
                    "generator": "intelligent_task_service",
                    "version": "1.0.0"
                }
            }
            
            # 保存为JSON文件
            json_path = os.path.join(output_path, f"{filename}.json")
            import json
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(output_content, f, ensure_ascii=False, indent=2)
            
            # 保存为YAML文件
            yaml_path = os.path.join(output_path, f"{filename}.yaml")
            import yaml
            with open(yaml_path, 'w', encoding='utf-8') as f:
                yaml.dump(output_content, f, default_flow_style=False, allow_unicode=True)
            
            # 生成Markdown报告
            markdown_path = os.path.join(output_path, f"{filename}.md")
            self._generate_markdown_report(output_content, markdown_path)
            
            self.logger.info(f"生成的任务配置已保存到: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"保存生成的任务配置失败: {e}")
            raise
    
    def _generate_markdown_report(self, output_content: Dict[str, Any], markdown_path: str):
        """
        生成Markdown报告
        
        Args:
            output_content: 输出内容
            markdown_path: Markdown文件路径
        """
        try:
            task_config = output_content['task_config']
            prediction = output_content['prediction']
            analysis = output_content['analysis']
            
            report_content = f"""# 智能任务生成报告

## 生成信息
- **生成时间**: {output_content['generated_at']}
- **原始描述**: {output_content['original_description']}
- **生成器版本**: {output_content['metadata']['version']}

## 任务配置

### 基本信息
- **任务ID**: {task_config.get('task_id', 'N/A')}
- **任务名称**: {task_config.get('name', 'N/A')}
- **任务类型**: {task_config.get('type', 'N/A')}
- **优先级**: {task_config.get('priority', 'N/A')}
- **描述**: {task_config.get('description', 'N/A')}

### AI配置
- **主模型**: {task_config.get('ai', {}).get('primary_model', 'N/A')}
- **模型**: {task_config.get('ai', {}).get('model', 'N/A')}
- **最大Token**: {task_config.get('ai', {}).get('max_tokens', 'N/A')}
- **温度**: {task_config.get('ai', {}).get('temperature', 'N/A')}

### 调度配置
- **调度类型**: {task_config.get('schedule', {}).get('type', 'N/A')}

### 超时配置
- **任务超时**: {task_config.get('timeout', {}).get('task_timeout', 'N/A')} 秒
- **AI超时**: {task_config.get('timeout', {}).get('ai_timeout', 'N/A')} 秒

## 预测结果

### 执行预测
- **预估执行时间**: {prediction['estimated_duration']} 分钟
- **成功概率**: {prediction['success_probability']:.2%}
- **复杂度评分**: {prediction['complexity_score']:.2f}

### 资源需求
- **CPU**: {prediction['resource_requirements'].get('cpu', 'N/A')}
- **内存**: {prediction['resource_requirements'].get('memory', 'N/A')}
- **磁盘**: {prediction['resource_requirements'].get('disk', 'N/A')}

### 风险因素
"""
            
            for risk in prediction['risk_factors']:
                report_content += f"- {risk}\n"
            
            report_content += """
### 优化建议
"""
            
            for suggestion in prediction['optimization_suggestions']:
                report_content += f"- {suggestion}\n"
            
            report_content += f"""
## 分析结果

### 任务分析
- **任务类型**: {analysis.get('task_type', 'N/A')}
- **复杂度**: {analysis.get('complexity', 'N/A')}
- **预估时间**: {analysis.get('estimated_duration', 'N/A')} 分钟
- **置信度**: {analysis.get('confidence_score', 'N/A')}

### 关键功能点
"""
            
            for feature in analysis.get('key_features', []):
                report_content += f"- {feature}\n"
            
            report_content += """
### 技术要求
"""
            
            for requirement in analysis.get('technical_requirements', []):
                report_content += f"- {requirement}\n"
            
            report_content += """
### 输出要求
"""
            
            for output_req in analysis.get('output_requirements', []):
                report_content += f"- {output_req}\n"
            
            report_content += """
### 相关标签
"""
            
            for tag in analysis.get('tags', []):
                report_content += f"- {tag}\n"
            
            report_content += """
## 使用说明

1. 检查生成的任务配置是否符合预期
2. 根据预测结果和优化建议调整配置
3. 将任务配置添加到任务管理器中
4. 执行任务并监控结果

## 注意事项

- 生成的任务配置仅供参考，建议根据实际情况进行调整
- 预测结果基于历史数据和模型分析，实际执行结果可能有所不同
- 建议在正式执行前进行小规模测试
"""
            
            with open(markdown_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
                
        except Exception as e:
            self.logger.error(f"生成Markdown报告失败: {e}")
            raise
    
    def _generate_execution_report(self, task_config: Dict[str, Any], prediction: Any,
                                  recommended_templates: List, analysis: Dict[str, Any],
                                  output_path: str) -> Dict[str, Any]:
        """
        生成执行报告
        
        Args:
            task_config: 任务配置
            prediction: 预测结果
            recommended_templates: 推荐模板
            analysis: 分析结果
            output_path: 输出路径
            
        Returns:
            执行报告
        """
        try:
            report = {
                "summary": {
                    "task_generated": True,
                    "task_id": task_config.get('task_id'),
                    "task_type": task_config.get('type'),
                    "complexity": analysis.get('complexity'),
                    "estimated_duration": prediction.estimated_duration,
                    "success_probability": prediction.success_probability
                },
                "details": {
                    "analysis": analysis,
                    "prediction": {
                        "estimated_duration": prediction.estimated_duration,
                        "success_probability": prediction.success_probability,
                        "complexity_score": prediction.complexity_score,
                        "risk_factors": prediction.risk_factors,
                        "optimization_suggestions": prediction.optimization_suggestions
                    },
                    "recommended_templates": [
                        {
                            "template_id": template.template_id,
                            "name": template.name,
                            "description": template.description,
                            "success_rate": template.success_rate,
                            "usage_count": template.usage_count
                        }
                        for template in recommended_templates
                    ]
                },
                "output": {
                    "path": output_path,
                    "files": [
                        f"generated_task_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        f"generated_task_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml",
                        f"generated_task_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                    ]
                },
                "recommendations": {
                    "next_steps": [
                        "检查生成的任务配置",
                        "根据预测结果调整参数",
                        "考虑使用推荐的模板",
                        "执行小规模测试"
                    ],
                    "warnings": prediction.risk_factors,
                    "suggestions": prediction.optimization_suggestions
                }
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"生成执行报告失败: {e}")
            return {
                "summary": {"task_generated": False, "error": str(e)},
                "details": {},
                "output": {"path": output_path},
                "recommendations": {"next_steps": ["检查错误信息"]}
            }
    
    def _validate_intelligent_task_config(self, config: Dict[str, Any]) -> List[str]:
        """
        验证智能任务生成配置
        
        Args:
            config: 配置字典
            
        Returns:
            错误列表
        """
        errors = []
        
        try:
            intelligent_task_config = config.get('intelligent_task', {})
            
            # 检查必需字段
            if not intelligent_task_config.get('description'):
                errors.append("智能任务生成配置缺少description字段")
            
            # 检查描述长度
            description = intelligent_task_config.get('description', '')
            if len(description) > 2000:
                errors.append("任务描述过长，建议控制在2000字符以内")
            
            # 检查输出配置
            output_config = config.get('output', {})
            if not output_config.get('output_path'):
                errors.append("缺少输出路径配置")
            
            return errors
            
        except Exception as e:
            errors.append(f"配置验证失败: {e}")
            return errors
