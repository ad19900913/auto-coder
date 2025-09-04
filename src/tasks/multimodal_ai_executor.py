"""
多模态AI支持任务执行器
负责图像处理、文档解析等多媒体内容处理任务
"""

import os
import json
import logging
from typing import Dict, Any, List
from datetime import datetime

from ..core.task_executor import TaskExecutor
from ..services.multimodal_ai_service import MultimodalAIService, MediaType, ProcessingType


class MultimodalAIExecutor(TaskExecutor):
    """多模态AI支持任务执行器"""
    
    def __init__(self, task_config: Dict[str, Any], services: Dict[str, Any]):
        super().__init__(task_config, services)
        self.multimodal_ai_service = services.get('multimodal_ai_service')
        self.logger = logging.getLogger(__name__)
    
    def _execute_task(self) -> Dict[str, Any]:
        """执行多模态AI支持任务"""
        multimodal_config = self.task_config.get('multimodal_ai', {})
        
        if not multimodal_config:
            raise ValueError("多模态AI任务缺少配置")
        
        operation = multimodal_config.get('operation')
        if not operation:
            raise ValueError("多模态AI任务缺少操作类型")
        
        self.logger.info(f"开始执行多模态AI操作: {operation}")
        
        try:
            if operation == 'process_single_file':
                result = self._process_single_file()
            elif operation == 'batch_process':
                result = self._batch_process()
            elif operation == 'analyze_media':
                result = self._analyze_media()
            elif operation == 'extract_content':
                result = self._extract_content()
            elif operation == 'convert_format':
                result = self._convert_format()
            elif operation == 'enhance_media':
                result = self._enhance_media()
            else:
                raise ValueError(f"不支持的操作类型: {operation}")
            
            # 生成执行报告
            report = self._generate_execution_report(operation, result)
            
            # 保存结果
            self._save_results(operation, result, report)
            
            return report
            
        except Exception as e:
            self.logger.error(f"多模态AI任务执行失败: {str(e)}")
            raise
    
    def _process_single_file(self) -> Dict[str, Any]:
        """处理单个文件"""
        config = self.task_config.get('multimodal_ai', {})
        file_path = config.get('file_path')
        processing_type = config.get('processing_type', 'analysis')
        options = config.get('options', {})
        
        if not file_path:
            raise ValueError("处理单个文件缺少file_path参数")
        
        if not os.path.exists(file_path):
            raise ValueError(f"文件不存在: {file_path}")
        
        # 转换处理类型
        processing_type_enum = ProcessingType(processing_type)
        
        # 处理文件
        result = self.multimodal_ai_service.process_media(file_path, processing_type_enum, options)
        
        return {
            'operation': 'process_single_file',
            'file_path': file_path,
            'processing_type': processing_type,
            'result': {
                'success': result.success,
                'media_type': result.media_type.value,
                'processing_time': result.processing_time,
                'extracted_text': result.extracted_text,
                'result_data': result.result_data,
                'error_message': result.error_message
            }
        }
    
    def _batch_process(self) -> Dict[str, Any]:
        """批量处理文件"""
        config = self.task_config.get('multimodal_ai', {})
        file_paths = config.get('file_paths', [])
        processing_type = config.get('processing_type', 'analysis')
        options = config.get('options', {})
        
        if not file_paths:
            raise ValueError("批量处理缺少file_paths参数")
        
        if not isinstance(file_paths, list):
            raise ValueError("file_paths必须是列表")
        
        # 验证文件存在性
        valid_files = []
        invalid_files = []
        for file_path in file_paths:
            if os.path.exists(file_path):
                valid_files.append(file_path)
            else:
                invalid_files.append(file_path)
        
        if not valid_files:
            raise ValueError("没有有效的文件可处理")
        
        # 转换处理类型
        processing_type_enum = ProcessingType(processing_type)
        
        # 批量处理
        results = self.multimodal_ai_service.batch_process(valid_files, processing_type_enum, options)
        
        # 统计结果
        success_count = sum(1 for r in results if r.success)
        total_count = len(results)
        
        return {
            'operation': 'batch_process',
            'file_paths': file_paths,
            'valid_files': valid_files,
            'invalid_files': invalid_files,
            'processing_type': processing_type,
            'statistics': {
                'total_files': total_count,
                'success_count': success_count,
                'failure_count': total_count - success_count,
                'success_rate': success_count / total_count if total_count > 0 else 0
            },
            'results': [
                {
                    'file_path': file_paths[i],
                    'success': r.success,
                    'media_type': r.media_type.value,
                    'processing_time': r.processing_time,
                    'extracted_text': r.extracted_text,
                    'error_message': r.error_message
                }
                for i, r in enumerate(results)
            ]
        }
    
    def _analyze_media(self) -> Dict[str, Any]:
        """分析媒体文件"""
        config = self.task_config.get('multimodal_ai', {})
        file_path = config.get('file_path')
        analysis_options = config.get('analysis_options', {})
        
        if not file_path:
            raise ValueError("分析媒体缺少file_path参数")
        
        if not os.path.exists(file_path):
            raise ValueError(f"文件不存在: {file_path}")
        
        # 使用分析处理类型
        result = self.multimodal_ai_service.process_media(
            file_path, ProcessingType.ANALYSIS, analysis_options
        )
        
        return {
            'operation': 'analyze_media',
            'file_path': file_path,
            'analysis_result': {
                'success': result.success,
                'media_type': result.media_type.value,
                'processing_time': result.processing_time,
                'analysis_data': result.result_data,
                'error_message': result.error_message
            }
        }
    
    def _extract_content(self) -> Dict[str, Any]:
        """提取内容"""
        config = self.task_config.get('multimodal_ai', {})
        file_path = config.get('file_path')
        extraction_options = config.get('extraction_options', {})
        
        if not file_path:
            raise ValueError("提取内容缺少file_path参数")
        
        if not os.path.exists(file_path):
            raise ValueError(f"文件不存在: {file_path}")
        
        # 使用提取处理类型
        result = self.multimodal_ai_service.process_media(
            file_path, ProcessingType.EXTRACTION, extraction_options
        )
        
        return {
            'operation': 'extract_content',
            'file_path': file_path,
            'extraction_result': {
                'success': result.success,
                'media_type': result.media_type.value,
                'processing_time': result.processing_time,
                'extracted_text': result.extracted_text,
                'extraction_data': result.result_data,
                'error_message': result.error_message
            }
        }
    
    def _convert_format(self) -> Dict[str, Any]:
        """转换格式"""
        config = self.task_config.get('multimodal_ai', {})
        file_path = config.get('file_path')
        conversion_options = config.get('conversion_options', {})
        
        if not file_path:
            raise ValueError("转换格式缺少file_path参数")
        
        if not os.path.exists(file_path):
            raise ValueError(f"文件不存在: {file_path}")
        
        # 使用转换处理类型
        result = self.multimodal_ai_service.process_media(
            file_path, ProcessingType.CONVERSION, conversion_options
        )
        
        return {
            'operation': 'convert_format',
            'file_path': file_path,
            'conversion_result': {
                'success': result.success,
                'media_type': result.media_type.value,
                'processing_time': result.processing_time,
                'conversion_data': result.result_data,
                'error_message': result.error_message
            }
        }
    
    def _enhance_media(self) -> Dict[str, Any]:
        """增强媒体"""
        config = self.task_config.get('multimodal_ai', {})
        file_path = config.get('file_path')
        enhancement_options = config.get('enhancement_options', {})
        
        if not file_path:
            raise ValueError("增强媒体缺少file_path参数")
        
        if not os.path.exists(file_path):
            raise ValueError(f"文件不存在: {file_path}")
        
        # 使用增强处理类型
        result = self.multimodal_ai_service.process_media(
            file_path, ProcessingType.ENHANCEMENT, enhancement_options
        )
        
        return {
            'operation': 'enhance_media',
            'file_path': file_path,
            'enhancement_result': {
                'success': result.success,
                'media_type': result.media_type.value,
                'processing_time': result.processing_time,
                'enhancement_data': result.result_data,
                'error_message': result.error_message
            }
        }
    
    def _generate_execution_report(self, operation: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """生成执行报告"""
        return {
            'task_id': self.task_config.get('task_id'),
            'operation': operation,
            'execution_time': datetime.now().isoformat(),
            'status': 'success' if self._check_success(result) else 'failed',
            'result': result,
            'summary': self._generate_summary(operation, result)
        }
    
    def _check_success(self, result: Dict[str, Any]) -> bool:
        """检查是否成功"""
        if 'result' in result:
            return result['result'].get('success', False)
        elif 'statistics' in result:
            return result['statistics'].get('success_count', 0) > 0
        elif 'analysis_result' in result:
            return result['analysis_result'].get('success', False)
        elif 'extraction_result' in result:
            return result['extraction_result'].get('success', False)
        elif 'conversion_result' in result:
            return result['conversion_result'].get('success', False)
        elif 'enhancement_result' in result:
            return result['enhancement_result'].get('success', False)
        return False
    
    def _generate_summary(self, operation: str, result: Dict[str, Any]) -> str:
        """生成操作摘要"""
        if operation == 'process_single_file':
            success = result.get('result', {}).get('success', False)
            file_path = result.get('file_path', '')
            return f"{'成功' if success else '失败'}处理文件: {file_path}"
        
        elif operation == 'batch_process':
            stats = result.get('statistics', {})
            total = stats.get('total_files', 0)
            success = stats.get('success_count', 0)
            return f"批量处理完成: {success}/{total} 个文件成功"
        
        elif operation == 'analyze_media':
            success = result.get('analysis_result', {}).get('success', False)
            file_path = result.get('file_path', '')
            return f"{'成功' if success else '失败'}分析媒体: {file_path}"
        
        elif operation == 'extract_content':
            success = result.get('extraction_result', {}).get('success', False)
            file_path = result.get('file_path', '')
            return f"{'成功' if success else '失败'}提取内容: {file_path}"
        
        elif operation == 'convert_format':
            success = result.get('conversion_result', {}).get('success', False)
            file_path = result.get('file_path', '')
            return f"{'成功' if success else '失败'}转换格式: {file_path}"
        
        elif operation == 'enhance_media':
            success = result.get('enhancement_result', {}).get('success', False)
            file_path = result.get('file_path', '')
            return f"{'成功' if success else '失败'}增强媒体: {file_path}"
        
        else:
            return f"执行操作: {operation}"
    
    def _save_results(self, operation: str, result: Dict[str, Any], report: Dict[str, Any]):
        """保存结果到文件"""
        output_config = self.task_config.get('output', {})
        output_path = output_config.get('output_path', './outputs/multimodal_ai')
        filename_template = output_config.get('filename_template', f'{operation}_{{timestamp}}')
        
        # 确保输出目录存在
        os.makedirs(output_path, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = filename_template.format(timestamp=timestamp)
        
        # 保存JSON格式
        json_path = os.path.join(output_path, f'{filename}.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 保存Markdown报告
        md_path = os.path.join(output_path, f'{filename}.md')
        self._generate_markdown_report(report, md_path)
        
        self.logger.info(f"结果已保存到: {json_path}, {md_path}")
    
    def _generate_markdown_report(self, report: Dict[str, Any], file_path: str):
        """生成Markdown报告"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"# 多模态AI支持任务执行报告\n\n")
            f.write(f"**任务ID**: {report.get('task_id')}\n")
            f.write(f"**操作类型**: {report.get('operation')}\n")
            f.write(f"**执行时间**: {report.get('execution_time')}\n")
            f.write(f"**状态**: {report.get('status')}\n\n")
            
            f.write("## 执行结果\n\n")
            result = report.get('result', {})
            
            if report.get('operation') == 'process_single_file':
                file_result = result.get('result', {})
                f.write(f"**文件路径**: {result.get('file_path')}\n")
                f.write(f"**处理类型**: {result.get('processing_type')}\n")
                f.write(f"**处理时间**: {file_result.get('processing_time', 0):.2f}s\n")
                f.write(f"**媒体类型**: {file_result.get('media_type')}\n")
                f.write(f"**处理结果**: {'成功' if file_result.get('success') else '失败'}\n\n")
                
                if file_result.get('extracted_text'):
                    f.write("### 提取的文本内容\n\n")
                    f.write(f"```\n{file_result.get('extracted_text')[:1000]}...\n```\n\n")
                
                if file_result.get('error_message'):
                    f.write("### 错误信息\n\n")
                    f.write(f"```\n{file_result.get('error_message')}\n```\n\n")
            
            elif report.get('operation') == 'batch_process':
                stats = result.get('statistics', {})
                f.write(f"**总文件数**: {stats.get('total_files', 0)}\n")
                f.write(f"**成功数**: {stats.get('success_count', 0)}\n")
                f.write(f"**失败数**: {stats.get('failure_count', 0)}\n")
                f.write(f"**成功率**: {stats.get('success_rate', 0):.2%}\n\n")
                
                f.write("### 处理结果详情\n\n")
                f.write("| 文件路径 | 状态 | 媒体类型 | 处理时间 |\n")
                f.write("|----------|------|----------|----------|\n")
                
                for file_result in result.get('results', []):
                    status = "成功" if file_result.get('success') else "失败"
                    f.write(f"| {file_result.get('file_path')} | {status} | {file_result.get('media_type')} | {file_result.get('processing_time', 0):.2f}s |\n")
            
            else:
                f.write(f"```json\n{json.dumps(result, ensure_ascii=False, indent=2)}\n```\n")
            
            f.write(f"\n## 摘要\n\n{report.get('summary', '')}\n")
    
    def _validate_multimodal_ai_config(self, config: Dict[str, Any]):
        """验证多模态AI配置"""
        multimodal_config = config.get('multimodal_ai', {})
        
        if not multimodal_config:
            raise ValueError("缺少multimodal_ai配置")
        
        operation = multimodal_config.get('operation')
        if not operation:
            raise ValueError("缺少操作类型")
        
        # 验证操作特定的参数
        if operation == 'process_single_file':
            if 'file_path' not in multimodal_config:
                raise ValueError("process_single_file操作缺少file_path参数")
        
        elif operation == 'batch_process':
            if 'file_paths' not in multimodal_config:
                raise ValueError("batch_process操作缺少file_paths参数")
            if not isinstance(multimodal_config['file_paths'], list):
                raise ValueError("file_paths必须是列表")
        
        elif operation in ['analyze_media', 'extract_content', 'convert_format', 'enhance_media']:
            if 'file_path' not in multimodal_config:
                raise ValueError(f"{operation}操作缺少file_path参数")
