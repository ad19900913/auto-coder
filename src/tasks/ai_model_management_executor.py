"""
AI模型管理任务执行器
负责模型注册、切换、性能监控等操作
"""

import os
import json
import logging
from typing import Dict, Any, List
from datetime import datetime

from ..core.task_executor import TaskExecutor
from ..services.ai_model_manager import AIModelManager, ModelType, ModelStatus


class AIModelManagementExecutor(TaskExecutor):
    """AI模型管理任务执行器"""
    
    def __init__(self, task_config: Dict[str, Any], services: Dict[str, Any]):
        super().__init__(task_config, services)
        self.ai_model_manager = services.get('ai_model_manager')
        self.logger = logging.getLogger(__name__)
    
    def _execute_task(self) -> Dict[str, Any]:
        """执行AI模型管理任务"""
        operation = self.task_config.get('ai_model_management', {}).get('operation')
        
        if not operation:
            raise ValueError("AI模型管理任务缺少操作类型")
        
        self.logger.info(f"开始执行AI模型管理操作: {operation}")
        
        try:
            if operation == 'register_model':
                result = self._register_model()
            elif operation == 'set_active_model':
                result = self._set_active_model()
            elif operation == 'list_models':
                result = self._list_models()
            elif operation == 'update_performance':
                result = self._update_performance()
            elif operation == 'get_statistics':
                result = self._get_statistics()
            elif operation == 'export_model':
                result = self._export_model()
            elif operation == 'import_model':
                result = self._import_model()
            elif operation == 'delete_model':
                result = self._delete_model()
            else:
                raise ValueError(f"不支持的操作类型: {operation}")
            
            # 生成执行报告
            report = self._generate_execution_report(operation, result)
            
            # 保存结果
            self._save_results(operation, result, report)
            
            return report
            
        except Exception as e:
            self.logger.error(f"AI模型管理任务执行失败: {str(e)}")
            raise
    
    def _register_model(self) -> Dict[str, Any]:
        """注册新模型"""
        config = self.task_config.get('ai_model_management', {})
        model_config = config.get('model_config', {})
        
        # 验证必要参数
        required_fields = ['model_name', 'model_type', 'version', 'provider']
        for field in required_fields:
            if field not in model_config:
                raise ValueError(f"注册模型缺少必要字段: {field}")
        
        # 注册模型
        version_id = self.ai_model_manager.register_model(
            model_name=model_config['model_name'],
            model_type=ModelType(model_config['model_type']),
            version=model_config['version'],
            provider=model_config['provider'],
            api_key=model_config.get('api_key'),
            endpoint=model_config.get('endpoint'),
            parameters=model_config.get('parameters', {})
        )
        
        # 如果指定为活跃模型，则设置为活跃
        if model_config.get('set_active', False):
            self.ai_model_manager.set_active_model(version_id)
        
        return {
            'operation': 'register_model',
            'version_id': version_id,
            'model_config': model_config,
            'success': True
        }
    
    def _set_active_model(self) -> Dict[str, Any]:
        """设置活跃模型"""
        config = self.task_config.get('ai_model_management', {})
        version_id = config.get('version_id')
        
        if not version_id:
            raise ValueError("设置活跃模型缺少version_id参数")
        
        success = self.ai_model_manager.set_active_model(version_id)
        
        return {
            'operation': 'set_active_model',
            'version_id': version_id,
            'success': success
        }
    
    def _list_models(self) -> Dict[str, Any]:
        """列出模型"""
        config = self.task_config.get('ai_model_management', {})
        model_type = config.get('model_type')
        status = config.get('status')
        
        # 转换枚举类型
        model_type_enum = ModelType(model_type) if model_type else None
        status_enum = ModelStatus(status) if status else None
        
        models = self.ai_model_manager.list_models(model_type_enum, status_enum)
        
        # 转换为可序列化的格式
        model_list = []
        for model in models:
            model_dict = {
                'version_id': model.version_id,
                'model_name': model.model_name,
                'model_type': model.model_type.value,
                'version': model.version,
                'provider': model.provider,
                'status': model.status.value,
                'usage_count': model.usage_count,
                'success_rate': model.success_rate,
                'avg_response_time': model.avg_response_time,
                'cost_per_request': model.cost_per_request,
                'created_at': model.created_at.isoformat(),
                'updated_at': model.updated_at.isoformat()
            }
            model_list.append(model_dict)
        
        return {
            'operation': 'list_models',
            'models': model_list,
            'total_count': len(model_list),
            'filters': {
                'model_type': model_type,
                'status': status
            }
        }
    
    def _update_performance(self) -> Dict[str, Any]:
        """更新模型性能"""
        config = self.task_config.get('ai_model_management', {})
        performance_data = config.get('performance_data', {})
        
        # 验证必要参数
        required_fields = ['version_id', 'response_time', 'success', 'cost', 'tokens_used']
        for field in required_fields:
            if field not in performance_data:
                raise ValueError(f"更新性能缺少必要字段: {field}")
        
        self.ai_model_manager.update_model_performance(
            version_id=performance_data['version_id'],
            response_time=performance_data['response_time'],
            success=performance_data['success'],
            cost=performance_data['cost'],
            tokens_used=performance_data['tokens_used'],
            error_message=performance_data.get('error_message')
        )
        
        return {
            'operation': 'update_performance',
            'version_id': performance_data['version_id'],
            'success': True
        }
    
    def _get_statistics(self) -> Dict[str, Any]:
        """获取模型统计信息"""
        stats = self.ai_model_manager.get_model_statistics()
        
        return {
            'operation': 'get_statistics',
            'statistics': stats
        }
    
    def _export_model(self) -> Dict[str, Any]:
        """导出模型配置"""
        config = self.task_config.get('ai_model_management', {})
        version_id = config.get('version_id')
        
        if not version_id:
            raise ValueError("导出模型缺少version_id参数")
        
        model_config = self.ai_model_manager.export_model_config(version_id)
        
        return {
            'operation': 'export_model',
            'version_id': version_id,
            'model_config': model_config
        }
    
    def _import_model(self) -> Dict[str, Any]:
        """导入模型配置"""
        config = self.task_config.get('ai_model_management', {})
        model_config = config.get('model_config', {})
        
        if not model_config:
            raise ValueError("导入模型缺少model_config参数")
        
        version_id = self.ai_model_manager.import_model_config(model_config)
        
        return {
            'operation': 'import_model',
            'version_id': version_id,
            'model_config': model_config,
            'success': True
        }
    
    def _delete_model(self) -> Dict[str, Any]:
        """删除模型"""
        config = self.task_config.get('ai_model_management', {})
        version_id = config.get('version_id')
        
        if not version_id:
            raise ValueError("删除模型缺少version_id参数")
        
        success = self.ai_model_manager.delete_model_version(version_id)
        
        return {
            'operation': 'delete_model',
            'version_id': version_id,
            'success': success
        }
    
    def _generate_execution_report(self, operation: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """生成执行报告"""
        return {
            'task_id': self.task_config.get('task_id'),
            'operation': operation,
            'execution_time': datetime.now().isoformat(),
            'status': 'success' if result.get('success', True) else 'failed',
            'result': result,
            'summary': self._generate_summary(operation, result)
        }
    
    def _generate_summary(self, operation: str, result: Dict[str, Any]) -> str:
        """生成操作摘要"""
        if operation == 'register_model':
            return f"成功注册模型版本: {result.get('version_id')}"
        elif operation == 'set_active_model':
            return f"{'成功' if result.get('success') else '失败'}设置活跃模型: {result.get('version_id')}"
        elif operation == 'list_models':
            return f"列出 {result.get('total_count', 0)} 个模型"
        elif operation == 'update_performance':
            return f"更新模型性能: {result.get('version_id')}"
        elif operation == 'get_statistics':
            return "获取模型统计信息"
        elif operation == 'export_model':
            return f"导出模型配置: {result.get('version_id')}"
        elif operation == 'import_model':
            return f"导入模型配置: {result.get('version_id')}"
        elif operation == 'delete_model':
            return f"{'成功' if result.get('success') else '失败'}删除模型: {result.get('version_id')}"
        else:
            return f"执行操作: {operation}"
    
    def _save_results(self, operation: str, result: Dict[str, Any], report: Dict[str, Any]):
        """保存结果到文件"""
        output_config = self.task_config.get('output', {})
        output_path = output_config.get('output_path', './outputs/ai_model_management')
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
            f.write(f"# AI模型管理任务执行报告\n\n")
            f.write(f"**任务ID**: {report.get('task_id')}\n")
            f.write(f"**操作类型**: {report.get('operation')}\n")
            f.write(f"**执行时间**: {report.get('execution_time')}\n")
            f.write(f"**状态**: {report.get('status')}\n\n")
            
            f.write("## 执行结果\n\n")
            result = report.get('result', {})
            
            if report.get('operation') == 'list_models':
                f.write(f"**模型总数**: {result.get('total_count', 0)}\n\n")
                f.write("### 模型列表\n\n")
                f.write("| 版本ID | 模型名称 | 类型 | 版本 | 提供商 | 状态 | 使用次数 | 成功率 |\n")
                f.write("|--------|----------|------|------|--------|------|----------|--------|\n")
                
                for model in result.get('models', []):
                    f.write(f"| {model.get('version_id')} | {model.get('model_name')} | {model.get('model_type')} | {model.get('version')} | {model.get('provider')} | {model.get('status')} | {model.get('usage_count')} | {model.get('success_rate', 0):.2%} |\n")
            
            elif report.get('operation') == 'get_statistics':
                stats = result.get('statistics', {})
                f.write(f"**总模型数**: {stats.get('total_models', 0)}\n")
                f.write(f"**活跃模型数**: {stats.get('active_models', 0)}\n\n")
                
                f.write("### 按类型统计\n\n")
                for model_type, type_stats in stats.get('model_types', {}).items():
                    f.write(f"**{model_type}**:\n")
                    f.write(f"- 总数: {type_stats.get('count', 0)}\n")
                    f.write(f"- 活跃: {type_stats.get('active', 0)}\n")
                    f.write(f"- 平均成功率: {type_stats.get('avg_success_rate', 0):.2%}\n")
                    f.write(f"- 平均响应时间: {type_stats.get('avg_response_time', 0):.2f}s\n\n")
            
            else:
                f.write(f"```json\n{json.dumps(result, ensure_ascii=False, indent=2)}\n```\n")
            
            f.write(f"\n## 摘要\n\n{report.get('summary', '')}\n")
    
    def _validate_ai_model_management_config(self, config: Dict[str, Any]):
        """验证AI模型管理配置"""
        ai_model_config = config.get('ai_model_management', {})
        
        if not ai_model_config:
            raise ValueError("缺少ai_model_management配置")
        
        operation = ai_model_config.get('operation')
        if not operation:
            raise ValueError("缺少操作类型")
        
        # 验证操作特定的参数
        if operation == 'register_model':
            model_config = ai_model_config.get('model_config', {})
            required_fields = ['model_name', 'model_type', 'version', 'provider']
            for field in required_fields:
                if field not in model_config:
                    raise ValueError(f"注册模型缺少必要字段: {field}")
        
        elif operation in ['set_active_model', 'export_model', 'delete_model']:
            if 'version_id' not in ai_model_config:
                raise ValueError(f"{operation}操作缺少version_id参数")
        
        elif operation == 'update_performance':
            performance_data = ai_model_config.get('performance_data', {})
            required_fields = ['version_id', 'response_time', 'success', 'cost', 'tokens_used']
            for field in required_fields:
                if field not in performance_data:
                    raise ValueError(f"更新性能缺少必要字段: {field}")
        
        elif operation == 'import_model':
            if 'model_config' not in ai_model_config:
                raise ValueError("导入模型缺少model_config参数")
