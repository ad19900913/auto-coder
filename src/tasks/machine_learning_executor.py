"""
机器学习集成任务执行器
提供预测模型、异常检测、智能调度和A/B测试功能的任务执行
"""

import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import asdict

from ..core.task_executor import TaskExecutor
from ..services.machine_learning_service import (
    MachineLearningService, TaskMetrics, PredictionResult, 
    AnomalyResult, ABTestConfig, ABTestResult
)


class MachineLearningExecutor(TaskExecutor):
    """机器学习集成任务执行器"""
    
    def __init__(self, task_config: Dict[str, Any], services: Dict[str, Any]):
        super().__init__(task_config, services)
        self.ml_service = services.get('machine_learning_service')
        self.logger = logging.getLogger(__name__)
    
    def _execute_task(self) -> Dict[str, Any]:
        """执行机器学习任务"""
        operation = self.task_config.get('machine_learning', {}).get('operation')
        
        if operation == 'predict_task':
            return self._predict_task_execution()
        elif operation == 'detect_anomalies':
            return self._detect_anomalies()
        elif operation == 'create_ab_test':
            return self._create_ab_test()
        elif operation == 'assign_variant':
            return self._assign_variant()
        elif operation == 'record_ab_result':
            return self._record_ab_test_result()
        elif operation == 'analyze_ab_test':
            return self._analyze_ab_test()
        elif operation == 'add_metrics':
            return self._add_task_metrics()
        elif operation == 'get_statistics':
            return self._get_model_statistics()
        elif operation == 'save_models':
            return self._save_models()
        elif operation == 'load_models':
            return self._load_models()
        elif operation == 'cleanup_data':
            return self._cleanup_old_data()
        else:
            raise ValueError(f"不支持的机器学习操作: {operation}")
    
    def _predict_task_execution(self) -> Dict[str, Any]:
        """预测任务执行"""
        task_config = self.task_config.get('machine_learning', {}).get('task_config', {})
        
        if not task_config:
            raise ValueError("预测任务执行需要提供task_config")
        
        # 进行预测
        prediction = self.ml_service.predict_task_execution(task_config)
        
        # 生成报告
        summary = f"任务执行预测完成: {prediction.task_id}"
        details = {
            'prediction': asdict(prediction),
            'task_config': task_config
        }
        
        return self._generate_execution_report(summary, details)
    
    def _detect_anomalies(self) -> Dict[str, Any]:
        """异常检测"""
        config = self.task_config.get('machine_learning', {})
        task_type = config.get('task_type')
        days = config.get('days', 30)
        
        # 获取任务指标
        metrics = self.ml_service.get_task_metrics(task_type, days)
        
        if len(metrics) < 10:
            summary = f"历史数据不足，无法进行异常检测: {len(metrics)}条"
            details = {'metrics_count': len(metrics), 'anomalies': []}
        else:
            # 进行异常检测
            anomalies = self.ml_service.detect_anomalies(metrics)
            
            summary = f"异常检测完成: 发现{len(anomalies)}个异常"
            details = {
                'metrics_count': len(metrics),
                'anomalies': [asdict(anomaly) for anomaly in anomalies]
            }
        
        return self._generate_execution_report(summary, details)
    
    def _create_ab_test(self) -> Dict[str, Any]:
        """创建A/B测试"""
        config = self.task_config.get('machine_learning', {})
        
        # 构建A/B测试配置
        ab_config = ABTestConfig(
            test_id=config.get('test_id'),
            name=config.get('name'),
            description=config.get('description'),
            variants=config.get('variants', {}),
            traffic_split=config.get('traffic_split', {}),
            metrics=config.get('metrics', []),
            duration_days=config.get('duration_days', 7),
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(days=config.get('duration_days', 7)),
            status='active'
        )
        
        # 创建A/B测试
        success = self.ml_service.create_ab_test(ab_config)
        
        if success:
            summary = f"A/B测试创建成功: {ab_config.test_id}"
            details = {'ab_test': asdict(ab_config)}
        else:
            summary = f"A/B测试创建失败: {ab_config.test_id}"
            details = {'error': 'A/B测试已存在或创建失败'}
        
        return self._generate_execution_report(summary, details)
    
    def _assign_variant(self) -> Dict[str, Any]:
        """分配A/B测试变体"""
        config = self.task_config.get('machine_learning', {})
        test_id = config.get('test_id')
        user_id = config.get('user_id')
        
        if not test_id or not user_id:
            raise ValueError("分配变体需要提供test_id和user_id")
        
        # 分配变体
        variant = self.ml_service.assign_variant(test_id, user_id)
        
        if variant:
            summary = f"变体分配成功: {test_id} -> {variant}"
            details = {'test_id': test_id, 'user_id': user_id, 'variant': variant}
        else:
            summary = f"变体分配失败: {test_id}"
            details = {'error': 'A/B测试不存在或未激活'}
        
        return self._generate_execution_report(summary, details)
    
    def _record_ab_test_result(self) -> Dict[str, Any]:
        """记录A/B测试结果"""
        config = self.task_config.get('machine_learning', {})
        test_id = config.get('test_id')
        variant = config.get('variant')
        metrics = config.get('metrics', {})
        sample_size = config.get('sample_size', 1)
        
        if not test_id or not variant:
            raise ValueError("记录A/B测试结果需要提供test_id和variant")
        
        # 记录结果
        self.ml_service.record_ab_test_result(test_id, variant, metrics, sample_size)
        
        summary = f"A/B测试结果记录成功: {test_id} - {variant}"
        details = {
            'test_id': test_id,
            'variant': variant,
            'metrics': metrics,
            'sample_size': sample_size
        }
        
        return self._generate_execution_report(summary, details)
    
    def _analyze_ab_test(self) -> Dict[str, Any]:
        """分析A/B测试结果"""
        config = self.task_config.get('machine_learning', {})
        test_id = config.get('test_id')
        
        if not test_id:
            raise ValueError("分析A/B测试需要提供test_id")
        
        # 分析结果
        results = self.ml_service.analyze_ab_test(test_id)
        
        summary = f"A/B测试分析完成: {test_id}"
        details = {
            'test_id': test_id,
            'results': [asdict(result) for result in results]
        }
        
        return self._generate_execution_report(summary, details)
    
    def _add_task_metrics(self) -> Dict[str, Any]:
        """添加任务指标"""
        config = self.task_config.get('machine_learning', {})
        
        # 构建任务指标
        metrics = TaskMetrics(
            task_id=config.get('task_id'),
            task_type=config.get('task_type'),
            duration=config.get('duration', 0.0),
            success=config.get('success', True),
            error_count=config.get('error_count', 0),
            retry_count=config.get('retry_count', 0),
            resource_usage=config.get('resource_usage', {}),
            timestamp=datetime.now(),
            features=config.get('features', {})
        )
        
        # 添加指标
        self.ml_service.add_task_metrics(metrics)
        
        summary = f"任务指标添加成功: {metrics.task_id}"
        details = {'metrics': asdict(metrics)}
        
        return self._generate_execution_report(summary, details)
    
    def _get_model_statistics(self) -> Dict[str, Any]:
        """获取模型统计信息"""
        # 获取统计信息
        stats = self.ml_service.get_model_statistics()
        
        summary = "模型统计信息获取成功"
        details = {'statistics': stats}
        
        return self._generate_execution_report(summary, details)
    
    def _save_models(self) -> Dict[str, Any]:
        """保存模型"""
        # 保存模型
        self.ml_service.save_models()
        
        summary = "模型保存成功"
        details = {'operation': 'save_models'}
        
        return self._generate_execution_report(summary, details)
    
    def _load_models(self) -> Dict[str, Any]:
        """加载模型"""
        # 加载模型
        self.ml_service.load_models()
        
        summary = "模型加载成功"
        details = {'operation': 'load_models'}
        
        return self._generate_execution_report(summary, details)
    
    def _cleanup_old_data(self) -> Dict[str, Any]:
        """清理旧数据"""
        config = self.task_config.get('machine_learning', {})
        days = config.get('days', 90)
        
        # 清理数据
        self.ml_service.cleanup_old_data(days)
        
        summary = f"旧数据清理完成: {days}天前"
        details = {'operation': 'cleanup_data', 'days': days}
        
        return self._generate_execution_report(summary, details)
    
    def _generate_execution_report(self, summary: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """生成执行报告"""
        return {
            'summary': summary,
            'details': details,
            'timestamp': datetime.now().isoformat(),
            'success': True
        }
    
    def _validate_machine_learning_config(self, config: Dict[str, Any]) -> List[str]:
        """验证机器学习配置"""
        errors = []
        
        if not config:
            errors.append("机器学习配置不能为空")
            return errors
        
        operation = config.get('operation')
        if not operation:
            errors.append("必须指定操作类型")
            return errors
        
        # 根据操作类型验证必要参数
        if operation == 'predict_task':
            if not config.get('task_config'):
                errors.append("预测任务执行需要提供task_config")
        
        elif operation == 'create_ab_test':
            if not config.get('test_id'):
                errors.append("创建A/B测试需要提供test_id")
            if not config.get('name'):
                errors.append("创建A/B测试需要提供name")
            if not config.get('variants'):
                errors.append("创建A/B测试需要提供variants")
        
        elif operation == 'assign_variant':
            if not config.get('test_id'):
                errors.append("分配变体需要提供test_id")
            if not config.get('user_id'):
                errors.append("分配变体需要提供user_id")
        
        elif operation == 'record_ab_result':
            if not config.get('test_id'):
                errors.append("记录A/B测试结果需要提供test_id")
            if not config.get('variant'):
                errors.append("记录A/B测试结果需要提供variant")
        
        elif operation == 'analyze_ab_test':
            if not config.get('test_id'):
                errors.append("分析A/B测试需要提供test_id")
        
        elif operation == 'add_metrics':
            if not config.get('task_id'):
                errors.append("添加任务指标需要提供task_id")
            if not config.get('task_type'):
                errors.append("添加任务指标需要提供task_type")
        
        return errors
