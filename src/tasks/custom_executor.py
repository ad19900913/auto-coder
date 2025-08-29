"""
自定义任务执行器 - 支持任意场景的AI任务执行
"""

import logging
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from ..core.task_executor import TaskExecutor


class CustomTaskExecutor(TaskExecutor):
    """自定义任务执行器，支持任意场景的AI任务执行"""
    
    def _execute_task(self) -> Dict[str, Any]:
        """
        执行自定义任务
        
        Returns:
            执行结果字典
        """
        try:
            self.logger.info(f"开始执行自定义任务: {self.task_id}")
            
            # 更新进度
            self._update_progress(10, "初始化自定义任务")
            
            # 获取任务配置
            custom_config = self.task_config.get('custom', {})
            task_objective = custom_config.get('objective')
            task_prompt = custom_config.get('prompt')
            output_format = custom_config.get('output_format', 'markdown')
            output_location = custom_config.get('output_location')
            
            if not all([task_objective, task_prompt]):
                raise ValueError("自定义任务配置不完整，缺少objective或prompt")
            
            # 更新进度
            self._update_progress(20, "分析任务目标")
            
            # 分析任务目标
            task_analysis = self._analyze_task_objective(task_objective, custom_config)
            
            # 更新进度
            self._update_progress(40, "执行AI任务")
            
            # 调用AI服务执行自定义任务
            ai_result = self.ai_service.execute_custom_task(
                prompt=task_prompt,
                task_type='custom',
                objective=task_objective,
                analysis=task_analysis
            )
            
            if not ai_result:
                raise RuntimeError("AI服务执行自定义任务失败")
            
            # 更新进度
            self._update_progress(60, "处理任务结果")
            
            # 处理AI任务结果
            processed_result = self._process_ai_result(ai_result, output_format, custom_config)
            
            # 更新进度
            self._update_progress(80, "保存任务结果")
            
            # 保存任务结果
            output_file = self._save_custom_task_result(
                processed_result, task_objective, output_format, output_location
            )
            
            # 更新进度
            self._update_progress(100, "自定义任务完成")
            
            # 准备执行结果
            result = {
                'success': True,
                'task_objective': task_objective,
                'output_format': output_format,
                'output_file': output_file,
                'ai_result_length': len(ai_result),
                'task_analysis': task_analysis
            }
            
            # 添加元数据
            self._add_metadata('custom_task_completed', True)
            self._add_metadata('task_objective', task_objective)
            self._add_metadata('output_format', output_format)
            self._add_metadata('ai_result_length', len(ai_result))
            
            self.logger.info(f"自定义任务执行成功: {self.task_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"自定义任务执行失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def _analyze_task_objective(self, objective: str, custom_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析任务目标
        
        Args:
            objective: 任务目标
            custom_config: 自定义配置
            
        Returns:
            任务分析结果
        """
        try:
            analysis = {
                'objective': objective,
                'task_type': 'custom',
                'complexity': 'medium',
                'estimated_duration': '5-10分钟',
                'required_resources': [],
                'output_requirements': []
            }
            
            # 分析任务复杂度
            if any(keyword in objective.lower() for keyword in ['分析', '分析', 'review', 'analyze']):
                analysis['complexity'] = 'high'
                analysis['estimated_duration'] = '10-20分钟'
            elif any(keyword in objective.lower() for keyword in ['生成', 'create', 'generate']):
                analysis['complexity'] = 'medium'
                analysis['estimated_duration'] = '5-15分钟'
            elif any(keyword in objective.lower() for keyword in ['转换', 'convert', 'transform']):
                analysis['complexity'] = 'low'
                analysis['estimated_duration'] = '3-8分钟'
            
            # 分析输出要求
            output_format = custom_config.get('output_format', 'markdown')
            if output_format == 'excel':
                analysis['output_requirements'].append('Excel格式输出')
            elif output_format == 'ppt':
                analysis['output_requirements'].append('PPT格式输出')
            elif output_format == 'markdown':
                analysis['output_requirements'].append('Markdown格式输出')
            
            # 分析任务类型
            if '代码' in objective or 'code' in objective.lower():
                analysis['task_type'] = 'code_related'
                analysis['required_resources'].append('代码分析能力')
            elif '文档' in objective or 'document' in objective.lower():
                analysis['task_type'] = 'document_related'
                analysis['required_resources'].append('文档处理能力')
            elif '数据' in objective or 'data' in objective.lower():
                analysis['task_type'] = 'data_related'
                analysis['required_resources'].append('数据分析能力')
            
            return analysis
            
        except Exception as e:
            self.logger.warning(f"分析任务目标失败: {e}")
            return {
                'objective': objective,
                'task_type': 'custom',
                'complexity': 'medium',
                'estimated_duration': '5-10分钟',
                'required_resources': [],
                'output_requirements': []
            }
    
    def _process_ai_result(self, ai_result: str, output_format: str, custom_config: Dict[str, Any]) -> str:
        """
        处理AI任务结果
        
        Args:
            ai_result: AI返回的结果
            output_format: 输出格式
            custom_config: 自定义配置
            
        Returns:
            处理后的结果
        """
        try:
            if output_format == 'markdown':
                return self._format_markdown_result(ai_result, custom_config)
            elif output_format == 'excel':
                return self._format_excel_result(ai_result, custom_config)
            elif output_format == 'ppt':
                return self._format_ppt_result(ai_result, custom_config)
            else:
                self.logger.warning(f"不支持的输出格式: {output_format}，使用markdown")
                return self._format_markdown_result(ai_result, custom_config)
                
        except Exception as e:
            self.logger.error(f"处理AI任务结果失败: {e}")
            return ai_result
    
    def _format_markdown_result(self, ai_result: str, custom_config: Dict[str, Any]) -> str:
        """
        格式化为Markdown结果
        
        Args:
            ai_result: AI返回的结果
            custom_config: 自定义配置
            
        Returns:
            Markdown格式的结果
        """
        try:
            task_objective = custom_config.get('objective', '自定义任务')
            
            # 添加结果头部信息
            header = f"""# {task_objective} 执行结果

> 自动执行时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
> 任务ID: {self.task_id}

---

"""
            
            # 如果结果已经包含标题，则直接返回
            if ai_result.strip().startswith('#'):
                return header + ai_result
            
            # 否则添加基本结构
            formatted_result = header + ai_result
            
            # 添加结果尾部
            footer = f"""

---

*本结果由AI自动生成，如有疑问请联系开发团队*
*生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
            
            return formatted_result + footer
            
        except Exception as e:
            self.logger.error(f"格式化Markdown结果失败: {e}")
            return ai_result
    
    def _format_excel_result(self, ai_result: str, custom_config: Dict[str, Any]) -> str:
        """
        格式化为Excel结果（返回Markdown，后续可转换为Excel）
        
        Args:
            ai_result: AI返回的结果
            custom_config: 自定义配置
            
        Returns:
            格式化的结果
        """
        try:
            # Excel格式暂时返回Markdown，后续可以通过pandas等库转换为Excel
            task_objective = custom_config.get('objective', '自定义任务')
            
            # 尝试将结果转换为表格格式
            table_result = self._convert_to_table_format(ai_result)
            
            header = f"""# {task_objective} 执行结果 (Excel格式)

> 自动执行时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
> 任务ID: {self.task_id}
> 输出格式: Excel (当前显示为Markdown表格)

---

"""
            
            return header + table_result
            
        except Exception as e:
            self.logger.error(f"格式化Excel结果失败: {e}")
            return self._format_markdown_result(ai_result, custom_config)
    
    def _format_ppt_result(self, ai_result: str, custom_config: Dict[str, Any]) -> str:
        """
        格式化为PPT结果（返回Markdown，后续可转换为PPT）
        
        Args:
            ai_result: AI返回的结果
            custom_config: 自定义配置
            
        Returns:
            格式化的结果
        """
        try:
            # PPT格式暂时返回Markdown，后续可以通过python-pptx等库转换为PPT
            task_objective = custom_config.get('objective', '自定义任务')
            
            # 将结果转换为幻灯片格式
            slide_result = self._convert_to_slide_format(ai_result)
            
            header = f"""# {task_objective} 执行结果 (PPT格式)

> 自动执行时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
> 任务ID: {self.task_id}
> 输出格式: PPT (当前显示为Markdown幻灯片)

---

"""
            
            return header + slide_result
            
        except Exception as e:
            self.logger.error(f"格式化PPT结果失败: {e}")
            return self._format_markdown_result(ai_result, custom_config)
    
    def _convert_to_table_format(self, content: str) -> str:
        """
        将内容转换为表格格式
        
        Args:
            content: 原始内容
            
        Returns:
            表格格式的内容
        """
        try:
            # 简单的表格转换逻辑
            lines = content.strip().split('\n')
            table_content = ""
            
            for i, line in enumerate(lines):
                if line.strip():
                    # 尝试识别列表项并转换为表格行
                    if line.strip().startswith('- ') or line.strip().startswith('* '):
                        item = line.strip()[2:]  # 移除列表标记
                        table_content += f"| {i+1} | {item} |\n"
                    elif line.strip().startswith('1. ') or line.strip().startswith('2. '):
                        parts = line.strip().split('. ', 1)
                        if len(parts) == 2:
                            table_content += f"| {parts[0]} | {parts[1]} |\n"
                    else:
                        # 普通行
                        table_content += f"| {i+1} | {line.strip()} |\n"
            
            if table_content:
                # 添加表格头部
                table_header = "| 序号 | 内容 |\n|------|------|\n"
                return table_header + table_content
            else:
                return content
                
        except Exception as e:
            self.logger.warning(f"转换为表格格式失败: {e}")
            return content
    
    def _convert_to_slide_format(self, content: str) -> str:
        """
        将内容转换为幻灯片格式
        
        Args:
            content: 原始内容
            
        Returns:
            幻灯片格式的内容
        """
        try:
            # 简单的幻灯片转换逻辑
            lines = content.strip().split('\n')
            slide_content = ""
            current_slide = 1
            
            for line in lines:
                if line.strip():
                    if line.strip().startswith('#'):
                        # 标题行作为新幻灯片
                        slide_content += f"\n## 幻灯片 {current_slide}\n\n"
                        slide_content += f"{line.strip()}\n\n"
                        current_slide += 1
                    else:
                        # 内容行
                        slide_content += f"{line.strip()}\n"
            
            if not slide_content.strip():
                # 如果没有标题，创建默认幻灯片
                slide_content = f"## 幻灯片 1\n\n{content}"
            
            return slide_content
            
        except Exception as e:
            self.logger.warning(f"转换为幻灯片格式失败: {e}")
            return content
    
    def _save_custom_task_result(self, content: str, task_objective: str, output_format: str, 
                                output_location: str = None) -> str:
        """
        保存自定义任务结果
        
        Args:
            content: 任务结果内容
            task_objective: 任务目标
            output_format: 输出格式
            output_location: 输出位置
            
        Returns:
            保存的文件路径
        """
        try:
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_objective = "".join(c for c in task_objective if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_objective = safe_objective.replace(' ', '_')[:30]  # 限制长度
            
            filename = f"{self.task_id}_{safe_objective}_{timestamp}.{self._get_file_extension(output_format)}"
            
            # 确定输出目录
            if output_location:
                if os.path.isabs(output_location):
                    output_dir = output_location
                else:
                    output_dir = os.path.join(os.getcwd(), output_location)
            else:
                # 使用默认输出目录
                output_dir = f"outputs/custom_tasks"
            
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            # 构建完整文件路径
            output_path = os.path.join(output_dir, filename)
            
            # 写入文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"自定义任务结果已保存到: {output_path}")
            
            # 添加到元数据
            self._add_metadata('output_file', output_path)
            self._add_metadata('output_directory', output_dir)
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"保存自定义任务结果失败: {e}")
            raise
    
    def _get_file_extension(self, output_format: str) -> str:
        """
        获取文件扩展名
        
        Args:
            output_format: 输出格式
            
        Returns:
            文件扩展名
        """
        format_extensions = {
            'markdown': 'md',
            'excel': 'md',  # 暂时使用md，后续可转换为xlsx
            'ppt': 'md',    # 暂时使用md，后续可转换为pptx
            'txt': 'txt'
        }
        
        return format_extensions.get(output_format.lower(), 'md')
    
    def _validate_custom_config(self, custom_config: Dict[str, Any]) -> List[str]:
        """
        验证自定义任务配置
        
        Args:
            custom_config: 自定义配置
            
        Returns:
            验证错误列表
        """
        errors = []
        
        # 检查必需字段
        if not custom_config.get('objective'):
            errors.append("自定义配置缺少必需字段: objective")
        
        if not custom_config.get('prompt'):
            errors.append("自定义配置缺少必需字段: prompt")
        
        # 检查输出格式
        output_format = custom_config.get('output_format')
        if output_format and output_format not in ['markdown', 'excel', 'ppt', 'txt']:
            errors.append(f"不支持的输出格式: {output_format}")
        
        return errors
    
    def _enhance_prompt_with_context(self, base_prompt: str, custom_config: Dict[str, Any]) -> str:
        """
        使用上下文信息增强提示
        
        Args:
            base_prompt: 基础提示
            custom_config: 自定义配置
            
        Returns:
            增强后的提示
        """
        try:
            enhanced_prompt = base_prompt
            
            # 添加任务目标
            objective = custom_config.get('objective', '')
            if objective:
                enhanced_prompt += f"\n\n任务目标: {objective}"
            
            # 添加输出格式要求
            output_format = custom_config.get('output_format', 'markdown')
            enhanced_prompt += f"\n\n请确保输出格式适合转换为: {output_format}"
            
            # 添加质量要求
            enhanced_prompt += "\n\n请确保结果内容准确、清晰、完整。"
            
            return enhanced_prompt
            
        except Exception as e:
            self.logger.warning(f"增强提示失败: {e}")
            return base_prompt
