"""
文档生成任务执行器 - 实现基于AI的文档自动生成
"""

import logging
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from ..core.task_executor import TaskExecutor


class DocTaskExecutor(TaskExecutor):
    """文档生成任务执行器，负责基于AI的文档自动生成"""
    
    def _execute_task(self) -> Dict[str, Any]:
        """
        执行文档生成任务
        
        Returns:
            执行结果字典
        """
        try:
            self.logger.info(f"开始执行文档生成任务: {self.task_id}")
            
            # 更新进度
            self._update_progress(10, "初始化文档生成任务")
            
            # 获取任务配置
            doc_config = self.task_config.get('doc', {})
            doc_type = doc_config.get('type', 'markdown')
            doc_prompt = doc_config.get('prompt')
            output_format = doc_config.get('output_format', 'markdown')
            output_location = doc_config.get('output_location')
            
            if not doc_prompt:
                raise ValueError("文档生成任务配置不完整，缺少prompt")
            
            # 更新进度
            self._update_progress(20, "分析文档需求")
            
            # 分析文档需求
            doc_requirements = self._analyze_doc_requirements(doc_prompt, doc_config)
            
            # 更新进度
            self._update_progress(40, "生成文档内容")
            
            # 调用AI服务生成文档
            generated_doc = self.ai_service.execute_custom_task(
                prompt=doc_prompt,
                task_type='doc_generation',
                doc_type=doc_type,
                requirements=doc_requirements
            )
            
            if not generated_doc:
                raise RuntimeError("AI服务生成文档失败")
            
            # 更新进度
            self._update_progress(60, "格式化文档")
            
            # 格式化文档内容
            formatted_doc = self._format_document(generated_doc, doc_type, output_format)
            
            # 更新进度
            self._update_progress(80, "保存文档")
            
            # 保存文档
            output_file = self._save_document(formatted_doc, doc_type, output_format, output_location)
            
            # 更新进度
            self._update_progress(100, "文档生成任务完成")
            
            # 准备执行结果
            result = {
                'success': True,
                'doc_type': doc_type,
                'output_format': output_format,
                'output_file': output_file,
                'doc_length': len(generated_doc),
                'requirements_analyzed': len(doc_requirements)
            }
            
            # 添加元数据
            self._add_metadata('doc_generated', True)
            self._add_metadata('doc_type', doc_type)
            self._add_metadata('output_format', output_format)
            self._add_metadata('doc_length', len(generated_doc))
            
            self.logger.info(f"文档生成任务执行成功: {self.task_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"文档生成任务执行失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def _analyze_doc_requirements(self, prompt: str, doc_config: Dict[str, Any]) -> List[str]:
        """
        分析文档需求
        
        Args:
            prompt: 文档生成提示
            doc_config: 文档配置
            
        Returns:
            需求列表
        """
        try:
            requirements = []
            
            # 基本需求分析
            doc_type = doc_config.get('type', 'markdown')
            requirements.append(f"文档类型: {doc_type}")
            
            # 分析提示中的关键信息
            if 'API' in prompt or '接口' in prompt:
                requirements.append("包含API接口文档")
            
            if '用户' in prompt or 'user' in prompt:
                requirements.append("包含用户使用说明")
            
            if '安装' in prompt or '部署' in prompt:
                requirements.append("包含安装部署说明")
            
            if '配置' in prompt or 'config' in prompt:
                requirements.append("包含配置说明")
            
            if '示例' in prompt or 'example' in prompt:
                requirements.append("包含使用示例")
            
            # 添加格式要求
            output_format = doc_config.get('output_format', 'markdown')
            requirements.append(f"输出格式: {output_format}")
            
            # 添加结构要求
            structure = doc_config.get('structure', [])
            if structure:
                requirements.append(f"文档结构: {', '.join(structure)}")
            
            return requirements
            
        except Exception as e:
            self.logger.warning(f"分析文档需求失败: {e}")
            return ["基本文档生成"]
    
    def _format_document(self, content: str, doc_type: str, output_format: str) -> str:
        """
        格式化文档内容
        
        Args:
            content: 原始文档内容
            doc_type: 文档类型
            output_format: 输出格式
            
        Returns:
            格式化后的文档内容
        """
        try:
            if output_format == 'markdown':
                return self._format_markdown(content, doc_type)
            elif output_format == 'html':
                return self._format_html(content, doc_type)
            elif output_format == 'word':
                return self._format_word(content, doc_type)
            else:
                self.logger.warning(f"不支持的输出格式: {output_format}，使用markdown")
                return self._format_markdown(content, doc_type)
                
        except Exception as e:
            self.logger.error(f"格式化文档失败: {e}")
            return content
    
    def _format_markdown(self, content: str, doc_type: str) -> str:
        """
        格式化为Markdown
        
        Args:
            content: 原始内容
            doc_type: 文档类型
            
        Returns:
            Markdown格式的文档
        """
        try:
            # 添加文档头部信息
            header = f"""# {doc_type.title()} 文档

> 自动生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
> 任务ID: {self.task_id}

---

"""
            
            # 如果内容已经包含标题，则直接返回
            if content.strip().startswith('#'):
                return header + content
            
            # 否则添加基本结构
            formatted_content = header + content
            
            # 添加文档尾部
            footer = f"""

---

*本文档由AI自动生成，如有疑问请联系开发团队*
*生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
            
            return formatted_content + footer
            
        except Exception as e:
            self.logger.error(f"格式化Markdown失败: {e}")
            return content
    
    def _format_html(self, content: str, doc_type: str) -> str:
        """
        格式化为HTML
        
        Args:
            content: 原始内容
            doc_type: 文档类型
            
        Returns:
            HTML格式的文档
        """
        try:
            # 简单的Markdown到HTML转换
            html_content = content.replace('\n\n', '</p><p>')
            html_content = html_content.replace('\n', '<br>')
            
            # 添加HTML结构
            html_doc = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{doc_type.title()} 文档</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; }}
        h1 {{ color: #333; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        .header {{ background: #f5f5f5; padding: 20px; border-radius: 5px; margin-bottom: 30px; }}
        .footer {{ margin-top: 50px; padding: 20px; background: #f9f9f9; border-radius: 5px; font-size: 0.9em; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{doc_type.title()} 文档</h1>
        <p><strong>自动生成时间:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        <p><strong>任务ID:</strong> {self.task_id}</p>
    </div>
    
    <div class="content">
        <p>{html_content}</p>
    </div>
    
    <div class="footer">
        <p><em>本文档由AI自动生成，如有疑问请联系开发团队</em></p>
        <p><em>生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</em></p>
    </div>
</body>
</html>"""
            
            return html_doc
            
        except Exception as e:
            self.logger.error(f"格式化HTML失败: {e}")
            return content
    
    def _format_word(self, content: str, doc_type: str) -> str:
        """
        格式化为Word文档（返回Markdown，后续可转换为Word）
        
        Args:
            content: 原始内容
            doc_type: 文档类型
            
        Returns:
            格式化的文档内容
        """
        try:
            # Word格式暂时返回Markdown，后续可以通过python-docx库转换为Word
            return self._format_markdown(content, doc_type)
            
        except Exception as e:
            self.logger.error(f"格式化Word文档失败: {e}")
            return content
    
    def _save_document(self, content: str, doc_type: str, output_format: str, 
                       output_location: str = None) -> str:
        """
        保存文档
        
        Args:
            content: 文档内容
            doc_type: 文档类型
            output_format: 输出格式
            output_location: 输出位置
            
        Returns:
            保存的文件路径
        """
        try:
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.task_id}_{doc_type}_{timestamp}.{self._get_file_extension(output_format)}"
            
            # 确定输出目录
            if output_location:
                if os.path.isabs(output_location):
                    output_dir = output_location
                else:
                    output_dir = os.path.join(os.getcwd(), output_location)
            else:
                # 使用默认输出目录
                output_dir = f"outputs/docs"
            
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            # 构建完整文件路径
            output_path = os.path.join(output_dir, filename)
            
            # 写入文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"文档已保存到: {output_path}")
            
            # 添加到元数据
            self._add_metadata('output_file', output_path)
            self._add_metadata('output_directory', output_dir)
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"保存文档失败: {e}")
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
            'html': 'html',
            'word': 'md',  # 暂时使用md，后续可转换为docx
            'txt': 'txt'
        }
        
        return format_extensions.get(output_format.lower(), 'md')
    
    def _validate_doc_config(self, doc_config: Dict[str, Any]) -> List[str]:
        """
        验证文档生成任务配置
        
        Args:
            doc_config: 文档配置
            
        Returns:
            验证错误列表
        """
        errors = []
        
        # 检查必需字段
        if not doc_config.get('prompt'):
            errors.append("文档配置缺少必需字段: prompt")
        
        # 检查文档类型
        doc_type = doc_config.get('type')
        if doc_type and doc_type not in ['markdown', 'html', 'word', 'txt']:
            errors.append(f"不支持的文档类型: {doc_type}")
        
        # 检查输出格式
        output_format = doc_config.get('output_format')
        if output_format and output_format not in ['markdown', 'html', 'word', 'txt']:
            errors.append(f"不支持的输出格式: {output_format}")
        
        return errors
    
    def _enhance_prompt_with_context(self, base_prompt: str, doc_config: Dict[str, Any]) -> str:
        """
        使用上下文信息增强提示
        
        Args:
            base_prompt: 基础提示
            doc_config: 文档配置
            
        Returns:
            增强后的提示
        """
        try:
            enhanced_prompt = base_prompt
            
            # 添加文档类型要求
            doc_type = doc_config.get('type', 'markdown')
            enhanced_prompt += f"\n\n请生成一个{doc_type}格式的文档。"
            
            # 添加结构要求
            structure = doc_config.get('structure', [])
            if structure:
                enhanced_prompt += f"\n\n文档应包含以下结构:\n" + "\n".join([f"- {item}" for item in structure])
            
            # 添加格式要求
            output_format = doc_config.get('output_format', 'markdown')
            if output_format != doc_type:
                enhanced_prompt += f"\n\n最终输出格式为: {output_format}"
            
            # 添加质量要求
            enhanced_prompt += "\n\n请确保文档内容准确、清晰、易于理解。"
            
            return enhanced_prompt
            
        except Exception as e:
            self.logger.warning(f"增强提示失败: {e}")
            return base_prompt
