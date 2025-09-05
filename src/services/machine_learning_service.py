"""
机器学习集成服务
提供预测模型、异常检测、智能调度和A/B测试功能
"""

import logging
import json
import os
import pymysql
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import pickle
import hashlib
from collections import defaultdict
import threading
import time

# 可选依赖
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    logging.warning("pandas未安装，部分机器学习功能将受限")

try:
    from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("scikit-learn未安装，机器学习功能将不可用")

try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False
    logging.warning("joblib未安装，模型持久化功能将受限")


class ModelType(Enum):
    """模型类型"""
    PREDICTION = "prediction"  # 预测模型
    ANOMALY_DETECTION = "anomaly_detection"  # 异常检测
    SCHEDULING = "scheduling"  # 智能调度
    AB_TESTING = "ab_testing"  # A/B测试


class TaskStatus(Enum):
    """任务状态"""
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class TaskMetrics:
    """任务指标"""
    task_id: str
    task_type: str
    duration: float  # 执行时间（秒）
    success: bool
    error_count: int
    retry_count: int
    resource_usage: Dict[str, float]  # CPU, 内存等资源使用
    timestamp: datetime
    features: Dict[str, Any]  # 特征数据


@dataclass
class PredictionResult:
    """预测结果"""
    task_id: str
    predicted_duration: float
    success_probability: float
    confidence: float
    risk_factors: List[str]
    recommendations: List[str]


@dataclass
class AnomalyResult:
    """异常检测结果"""
    task_id: str
    is_anomaly: bool
    anomaly_score: float
    anomaly_type: str
    severity: str  # low, medium, high
    explanation: str


@dataclass
class ABTestConfig:
    """A/B测试配置"""
    test_id: str
    name: str
    description: str
    variants: Dict[str, Dict[str, Any]]  # 变体配置
    traffic_split: Dict[str, float]  # 流量分配
    metrics: List[str]  # 监控指标
    duration_days: int
    start_time: datetime
    end_time: datetime
    status: str  # active, completed, paused


@dataclass
class ABTestResult:
    """A/B测试结果"""
    test_id: str
    variant: str
    metrics: Dict[str, float]
    sample_size: int
    confidence_interval: Tuple[float, float]
    p_value: float
    is_significant: bool
    winner: Optional[str]


class MachineLearningService:
    """机器学习服务"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 检查依赖
        self._check_dependencies()
        
        # MySQL数据库配置
        self.db_config = config.get('database', {})
        self.host = self.db_config.get('host', 'localhost')
        self.port = self.db_config.get('port', 3306)
        self.user = self.db_config.get('user', 'root')
        self.password = self.db_config.get('password', '')
        self.database = self.db_config.get('database', 'auto_coder')
        self.charset = self.db_config.get('charset', 'utf8mb4')
        
        # 初始化数据库
        self._init_database()
        
        # 模型存储路径
        self.models_dir = config.get('models_directory', './models')
        os.makedirs(self.models_dir, exist_ok=True)
        
        # 缓存
        self._models_cache = {}
        self._scaler_cache = {}
        self._lock = threading.Lock()
        
        # 配置
        self.prediction_config = config.get('prediction', {})
        self.anomaly_config = config.get('anomaly_detection', {})
        self.scheduling_config = config.get('scheduling', {})
        self.ab_testing_config = config.get('ab_testing', {})
        
        self.logger.info("机器学习服务初始化完成")
    
    def _check_dependencies(self):
        """检查依赖库"""
        if not SKLEARN_AVAILABLE:
            self.logger.warning("scikit-learn未安装，机器学习功能将受限")
            # 不抛出异常，允许在没有scikit-learn的情况下运行
        
        if not PANDAS_AVAILABLE:
            self.logger.warning("pandas未安装，数据处理功能受限")
        
        if not JOBLIB_AVAILABLE:
            self.logger.warning("joblib未安装，模型持久化功能受限")
    
    def _init_database(self):
        """初始化数据库"""
        try:
            # 创建数据库连接
            conn = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                charset=self.charset,
                autocommit=True
            )
            cursor = conn.cursor()
            
            # 创建数据库（如果不存在）
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{self.database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            cursor.execute(f"USE `{self.database}`")
            
            # 任务指标表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS task_metrics (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    task_id VARCHAR(255) NOT NULL,
                    task_type VARCHAR(100) NOT NULL,
                    duration DECIMAL(10,3) NOT NULL,
                    success TINYINT NOT NULL,
                    error_count INT NOT NULL,
                    retry_count INT NOT NULL,
                    resource_usage TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    features TEXT NOT NULL,
                    created_at DATETIME NOT NULL,
                    INDEX idx_task_id (task_id),
                    INDEX idx_timestamp (timestamp)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            ''')
            
            # 预测结果表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predictions (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    task_id VARCHAR(255) NOT NULL,
                    predicted_duration DECIMAL(10,3) NOT NULL,
                    success_probability DECIMAL(5,4) NOT NULL,
                    confidence DECIMAL(5,4) NOT NULL,
                    risk_factors TEXT NOT NULL,
                    recommendations TEXT NOT NULL,
                    actual_duration DECIMAL(10,3),
                    actual_success TINYINT,
                    created_at DATETIME NOT NULL,
                    INDEX idx_task_id (task_id),
                    INDEX idx_created_at (created_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            ''')
            
            # 异常检测结果表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS anomalies (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    task_id VARCHAR(255) NOT NULL,
                    is_anomaly TINYINT NOT NULL,
                    anomaly_score DECIMAL(10,6) NOT NULL,
                    anomaly_type VARCHAR(100) NOT NULL,
                    severity VARCHAR(50) NOT NULL,
                    explanation TEXT NOT NULL,
                    created_at DATETIME NOT NULL,
                    INDEX idx_task_id (task_id),
                    INDEX idx_created_at (created_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            ''')
            
            # A/B测试配置表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ab_tests (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    test_id VARCHAR(255) UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    description TEXT NOT NULL,
                    variants TEXT NOT NULL,
                    traffic_split TEXT NOT NULL,
                    metrics TEXT NOT NULL,
                    duration_days INT NOT NULL,
                    start_time DATETIME NOT NULL,
                    end_time DATETIME NOT NULL,
                    status VARCHAR(50) NOT NULL,
                    created_at DATETIME NOT NULL,
                    INDEX idx_test_id (test_id),
                    INDEX idx_status (status)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            ''')
            
            # A/B测试结果表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ab_test_results (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    test_id VARCHAR(255) NOT NULL,
                    variant VARCHAR(100) NOT NULL,
                    metrics TEXT NOT NULL,
                    sample_size INT NOT NULL,
                    confidence_interval TEXT NOT NULL,
                    p_value DECIMAL(10,6) NOT NULL,
                    is_significant TINYINT NOT NULL,
                    winner VARCHAR(100),
                    created_at DATETIME NOT NULL,
                    INDEX idx_test_id (test_id),
                    FOREIGN KEY (test_id) REFERENCES ab_tests (test_id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            ''')
            
            conn.close()
            self.logger.info("MySQL数据库初始化完成")
            
        except Exception as e:
            self.logger.error(f"数据库初始化失败: {e}")
            raise
    
    def _get_connection(self):
        """获取MySQL数据库连接"""
        return pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            charset=self.charset,
            autocommit=True
        )
    
    def add_task_metrics(self, metrics: TaskMetrics):
        """添加任务指标"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO task_metrics 
                (task_id, task_type, duration, success, error_count, retry_count, 
                 resource_usage, timestamp, features, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                metrics.task_id,
                metrics.task_type,
                metrics.duration,
                int(metrics.success),
                metrics.error_count,
                metrics.retry_count,
                json.dumps(metrics.resource_usage),
                metrics.timestamp,
                json.dumps(metrics.features),
                datetime.now()
            ))
        
        self.logger.info(f"添加任务指标: {metrics.task_id}")
    
    def get_task_metrics(self, task_type: Optional[str] = None, 
                        days: int = 30) -> List[TaskMetrics]:
        """获取任务指标"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT task_id, task_type, duration, success, error_count, retry_count,
                       resource_usage, timestamp, features
                FROM task_metrics
                WHERE timestamp >= %s
            '''
            params = [datetime.now() - timedelta(days=days)]
            
            if task_type:
                query += ' AND task_type = %s'
                params.append(task_type)
            
            query += ' ORDER BY timestamp DESC'
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
        
        metrics = []
        for row in rows:
            metrics.append(TaskMetrics(
                task_id=row[0],
                task_type=row[1],
                duration=row[2],
                success=bool(row[3]),
                error_count=row[4],
                retry_count=row[5],
                resource_usage=json.loads(row[6]),
                timestamp=row[7] if isinstance(row[7], datetime) else datetime.fromisoformat(row[7]),
                features=json.loads(row[8])
            ))
        
        return metrics
    
    def predict_task_execution(self, task_config: Dict[str, Any]) -> PredictionResult:
        """预测任务执行"""
        if not SKLEARN_AVAILABLE:
            return self._default_prediction(task_config)
        
        # 提取特征
        features = self._extract_task_features(task_config)
        
        # 获取历史数据
        task_type = task_config.get('type', 'unknown')
        historical_metrics = self.get_task_metrics(task_type, days=90)
        
        if len(historical_metrics) < 10:
            self.logger.warning(f"历史数据不足，使用默认预测: {len(historical_metrics)}条")
            return self._default_prediction(task_config)
        
        # 训练预测模型
        model = self._train_prediction_model(historical_metrics)
        
        # 进行预测
        prediction = self._make_prediction(model, features, historical_metrics)
        
        # 保存预测结果
        self._save_prediction(prediction)
        
        return prediction
    
    def _extract_task_features(self, task_config: Dict[str, Any]) -> Dict[str, Any]:
        """提取任务特征"""
        features = {
            'task_type': task_config.get('type', 'unknown'),
            'priority': task_config.get('priority', 5),
            'has_schedule': int('schedule' in task_config),
            'has_dependencies': int('dependencies' in task_config),
            'has_resources': int('resources' in task_config),
            'retry_enabled': int(task_config.get('retry', {}).get('max_attempts', 0) > 0),
            'timeout_set': int(task_config.get('timeout', {}).get('task_timeout', 0) > 0),
            'notify_enabled': int(task_config.get('notify', {}).get('on_complete', False)),
            'config_complexity': len(str(task_config)),
        }
        
        # 添加调度特征
        if 'schedule' in task_config:
            schedule = task_config['schedule']
            features.update({
                'schedule_type': schedule.get('type', 'manual'),
                'is_cron': int('cron_expression' in schedule or 'expression' in schedule),
                'is_interval': int('interval' in schedule),
            })
        
        # 添加依赖特征
        if 'dependencies' in task_config:
            deps = task_config['dependencies']
            features.update({
                'dependency_count': len(deps),
                'has_required_deps': int(any(d.get('type') == 'required' for d in deps)),
                'has_optional_deps': int(any(d.get('type') == 'optional' for d in deps)),
            })
        
        # 添加资源特征
        if 'resources' in task_config:
            resources = task_config['resources']
            features.update({
                'cpu_required': resources.get('cpu', 1),
                'memory_required': resources.get('memory', 512),
                'disk_required': resources.get('disk', 100),
            })
        
        return features
    
    def _train_prediction_model(self, metrics: List[TaskMetrics]) -> Any:
        """训练预测模型"""
        # 准备训练数据
        X = []
        y_duration = []
        y_success = []
        
        for metric in metrics:
            features = metric.features
            feature_vector = [
                features.get('priority', 5),
                features.get('has_schedule', 0),
                features.get('has_dependencies', 0),
                features.get('has_resources', 0),
                features.get('retry_enabled', 0),
                features.get('timeout_set', 0),
                features.get('notify_enabled', 0),
                features.get('config_complexity', 0),
                features.get('dependency_count', 0),
                features.get('cpu_required', 1),
                features.get('memory_required', 512),
                features.get('disk_required', 100),
            ]
            
            X.append(feature_vector)
            y_duration.append(metric.duration)
            y_success.append(int(metric.success))
        
        X = np.array(X)
        y_duration = np.array(y_duration)
        y_success = np.array(y_success)
        
        # 标准化特征
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # 训练持续时间预测模型
        duration_model = RandomForestRegressor(n_estimators=100, random_state=42)
        duration_model.fit(X_scaled, y_duration)
        
        # 训练成功率预测模型
        success_model = RandomForestClassifier(n_estimators=100, random_state=42)
        success_model.fit(X_scaled, y_success)
        
        # 缓存模型和标准化器
        with self._lock:
            self._models_cache['duration'] = duration_model
            self._models_cache['success'] = success_model
            self._scaler_cache['scaler'] = scaler
        
        return {
            'duration_model': duration_model,
            'success_model': success_model,
            'scaler': scaler
        }
    
    def _make_prediction(self, model: Dict[str, Any], features: Dict[str, Any], 
                        historical_metrics: List[TaskMetrics]) -> PredictionResult:
        """进行预测"""
        # 准备特征向量
        feature_vector = [
            features.get('priority', 5),
            features.get('has_schedule', 0),
            features.get('has_dependencies', 0),
            features.get('has_resources', 0),
            features.get('retry_enabled', 0),
            features.get('timeout_set', 0),
            features.get('notify_enabled', 0),
            features.get('config_complexity', 0),
            features.get('dependency_count', 0),
            features.get('cpu_required', 1),
            features.get('memory_required', 512),
            features.get('disk_required', 100),
        ]
        
        X = np.array([feature_vector])
        X_scaled = model['scaler'].transform(X)
        
        # 预测持续时间
        predicted_duration = model['duration_model'].predict(X_scaled)[0]
        
        # 预测成功率
        success_proba = model['success_model'].predict_proba(X_scaled)[0]
        success_probability = success_proba[1]  # 成功概率
        
        # 计算置信度
        confidence = self._calculate_confidence(model, X_scaled)
        
        # 识别风险因素
        risk_factors = self._identify_risk_factors(features, historical_metrics)
        
        # 生成建议
        recommendations = self._generate_recommendations(features, predicted_duration, 
                                                       success_probability, risk_factors)
        
        return PredictionResult(
            task_id=features.get('task_id', 'unknown'),
            predicted_duration=predicted_duration,
            success_probability=success_probability,
            confidence=confidence,
            risk_factors=risk_factors,
            recommendations=recommendations
        )
    
    def _calculate_confidence(self, model: Dict[str, Any], X_scaled: np.ndarray) -> float:
        """计算预测置信度"""
        # 使用随机森林的预测方差作为置信度指标
        duration_predictions = []
        for estimator in model['duration_model'].estimators_:
            duration_predictions.append(estimator.predict(X_scaled)[0])
        
        # 计算预测的标准差，转换为置信度（0-1）
        std = np.std(duration_predictions)
        mean = np.mean(duration_predictions)
        cv = std / mean if mean > 0 else 1.0
        
        # 将变异系数转换为置信度
        confidence = max(0.0, min(1.0, 1.0 - cv))
        return confidence
    
    def _identify_risk_factors(self, features: Dict[str, Any], 
                              historical_metrics: List[TaskMetrics]) -> List[str]:
        """识别风险因素"""
        risk_factors = []
        
        # 分析历史数据
        if historical_metrics:
            success_rate = sum(1 for m in historical_metrics if m.success) / len(historical_metrics)
            avg_duration = np.mean([m.duration for m in historical_metrics])
            
            if success_rate < 0.8:
                risk_factors.append("历史成功率较低")
            
            if features.get('has_dependencies', 0) and features.get('dependency_count', 0) > 3:
                risk_factors.append("依赖关系复杂")
            
            if features.get('priority', 5) > 7:
                risk_factors.append("任务优先级较高")
            
            if features.get('config_complexity', 0) > 1000:
                risk_factors.append("配置复杂度较高")
        
        return risk_factors
    
    def _generate_recommendations(self, features: Dict[str, Any], 
                                predicted_duration: float, success_probability: float,
                                risk_factors: List[str]) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        if success_probability < 0.8:
            recommendations.append("建议增加重试次数以提高成功率")
        
        if predicted_duration > 300:  # 5分钟
            recommendations.append("预计执行时间较长，建议优化任务配置")
        
        if features.get('has_dependencies', 0) and features.get('dependency_count', 0) > 3:
            recommendations.append("依赖关系较多，建议简化依赖结构")
        
        if not features.get('timeout_set', 0):
            recommendations.append("建议设置任务超时时间")
        
        if not features.get('retry_enabled', 0):
            recommendations.append("建议启用重试机制")
        
        return recommendations
    
    def _default_prediction(self, task_config: Dict[str, Any]) -> PredictionResult:
        """默认预测（当机器学习不可用时）"""
        task_type = task_config.get('type', 'unknown')
        
        # 基于任务类型的简单预测
        default_durations = {
            'coding': 1800,  # 30分钟
            'review': 600,   # 10分钟
            'doc': 900,      # 15分钟
            'custom': 1200,  # 20分钟
        }
        
        predicted_duration = default_durations.get(task_type, 600)
        success_probability = 0.85  # 默认成功率
        
        return PredictionResult(
            task_id=task_config.get('task_id', 'unknown'),
            predicted_duration=predicted_duration,
            success_probability=success_probability,
            confidence=0.5,
            risk_factors=["使用默认预测模型"],
            recommendations=["建议收集更多历史数据以启用机器学习预测"]
        )
    
    def _save_prediction(self, prediction: PredictionResult):
        """保存预测结果"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO predictions 
                (task_id, predicted_duration, success_probability, confidence,
                 risk_factors, recommendations, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                prediction.task_id,
                prediction.predicted_duration,
                prediction.success_probability,
                prediction.confidence,
                json.dumps(prediction.risk_factors),
                json.dumps(prediction.recommendations),
                datetime.now().isoformat()
            ))
            conn.commit()
    
    def detect_anomalies(self, task_metrics: List[TaskMetrics]) -> List[AnomalyResult]:
        """异常检测"""
        if not SKLEARN_AVAILABLE or len(task_metrics) < 10:
            return []
        
        anomalies = []
        
        # 提取数值特征
        durations = [m.duration for m in task_metrics]
        error_counts = [m.error_count for m in task_metrics]
        retry_counts = [m.retry_count for m in task_metrics]
        
        # 计算统计指标
        duration_mean = np.mean(durations)
        duration_std = np.std(durations)
        error_mean = np.mean(error_counts)
        error_std = np.std(error_counts)
        
        # 异常检测阈值
        duration_threshold = 2.0  # 2个标准差
        error_threshold = 2.0
        
        for metric in task_metrics:
            anomaly_score = 0.0
            anomaly_type = "normal"
            severity = "low"
            explanations = []
            
            # 检查执行时间异常
            if abs(metric.duration - duration_mean) > duration_threshold * duration_std:
                anomaly_score += 0.4
                anomaly_type = "duration_anomaly"
                explanations.append(f"执行时间异常: {metric.duration:.2f}s (平均: {duration_mean:.2f}s)")
            
            # 检查错误次数异常
            if abs(metric.error_count - error_mean) > error_threshold * error_std:
                anomaly_score += 0.3
                if anomaly_type == "normal":
                    anomaly_type = "error_anomaly"
                explanations.append(f"错误次数异常: {metric.error_count} (平均: {error_mean:.2f})")
            
            # 检查重试次数异常
            if metric.retry_count > 3:
                anomaly_score += 0.2
                if anomaly_type == "normal":
                    anomaly_type = "retry_anomaly"
                explanations.append(f"重试次数过多: {metric.retry_count}")
            
            # 检查任务失败
            if not metric.success:
                anomaly_score += 0.5
                if anomaly_type == "normal":
                    anomaly_type = "failure"
                explanations.append("任务执行失败")
            
            # 确定严重程度
            if anomaly_score >= 0.8:
                severity = "high"
            elif anomaly_score >= 0.5:
                severity = "medium"
            
            if anomaly_score > 0.3:  # 只报告明显的异常
                anomaly = AnomalyResult(
                    task_id=metric.task_id,
                    is_anomaly=True,
                    anomaly_score=anomaly_score,
                    anomaly_type=anomaly_type,
                    severity=severity,
                    explanation="; ".join(explanations)
                )
                anomalies.append(anomaly)
                
                # 保存异常检测结果
                self._save_anomaly(anomaly)
        
        return anomalies
    
    def _save_anomaly(self, anomaly: AnomalyResult):
        """保存异常检测结果"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO anomalies 
                (task_id, is_anomaly, anomaly_score, anomaly_type, severity, explanation, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                anomaly.task_id,
                int(anomaly.is_anomaly),
                anomaly.anomaly_score,
                anomaly.anomaly_type,
                anomaly.severity,
                anomaly.explanation,
                datetime.now().isoformat()
            ))
            conn.commit()
    
    def create_ab_test(self, config: ABTestConfig) -> bool:
        """创建A/B测试"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO ab_tests 
                    (test_id, name, description, variants, traffic_split, metrics,
                     duration_days, start_time, end_time, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    config.test_id,
                    config.name,
                    config.description,
                    json.dumps(config.variants),
                    json.dumps(config.traffic_split),
                    json.dumps(config.metrics),
                    config.duration_days,
                    config.start_time.isoformat(),
                    config.end_time.isoformat(),
                    config.status,
                    datetime.now().isoformat()
                ))
                conn.commit()
            
            self.logger.info(f"A/B测试创建成功: {config.test_id}")
            return True
        except sqlite3.IntegrityError:
            self.logger.error(f"A/B测试已存在: {config.test_id}")
            return False
        except Exception as e:
            self.logger.error(f"创建A/B测试失败: {e}")
            return False
    
    def get_ab_test(self, test_id: str) -> Optional[ABTestConfig]:
        """获取A/B测试配置"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT name, description, variants, traffic_split, metrics,
                       duration_days, start_time, end_time, status
                FROM ab_tests WHERE test_id = ?
            ''', (test_id,))
            row = cursor.fetchone()
        
        if row:
            return ABTestConfig(
                test_id=test_id,
                name=row[0],
                description=row[1],
                variants=json.loads(row[2]),
                traffic_split=json.loads(row[3]),
                metrics=json.loads(row[4]),
                duration_days=row[5],
                start_time=datetime.fromisoformat(row[6]),
                end_time=datetime.fromisoformat(row[7]),
                status=row[8]
            )
        return None
    
    def assign_variant(self, test_id: str, user_id: str) -> Optional[str]:
        """分配A/B测试变体"""
        config = self.get_ab_test(test_id)
        if not config or config.status != 'active':
            return None
        
        # 使用用户ID的哈希值进行一致性分配
        hash_value = int(hashlib.md5(f"{test_id}:{user_id}".encode()).hexdigest()[:8], 16)
        hash_ratio = hash_value / (16 ** 8)  # 转换为0-1之间的值
        
        # 根据流量分配选择变体
        cumulative_prob = 0.0
        for variant, probability in config.traffic_split.items():
            cumulative_prob += probability
            if hash_ratio <= cumulative_prob:
                return variant
        
        return list(config.variants.keys())[0]  # 默认返回第一个变体
    
    def record_ab_test_result(self, test_id: str, variant: str, 
                            metrics: Dict[str, float], sample_size: int):
        """记录A/B测试结果"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO ab_test_results 
                    (test_id, variant, metrics, sample_size, confidence_interval,
                     p_value, is_significant, winner, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    test_id,
                    variant,
                    json.dumps(metrics),
                    sample_size,
                    json.dumps([0.0, 0.0]),  # 简化的置信区间
                    0.05,  # 简化的p值
                    0,  # 简化的是否显著
                    None,  # 胜者
                    datetime.now().isoformat()
                ))
                conn.commit()
            
            self.logger.info(f"A/B测试结果记录成功: {test_id} - {variant}")
        except Exception as e:
            self.logger.error(f"记录A/B测试结果失败: {e}")
    
    def analyze_ab_test(self, test_id: str) -> List[ABTestResult]:
        """分析A/B测试结果"""
        config = self.get_ab_test(test_id)
        if not config:
            return []
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT variant, metrics, sample_size, confidence_interval,
                       p_value, is_significant, winner
                FROM ab_test_results WHERE test_id = ?
            ''', (test_id,))
            rows = cursor.fetchall()
        
        results = []
        for row in rows:
            results.append(ABTestResult(
                test_id=test_id,
                variant=row[0],
                metrics=json.loads(row[1]),
                sample_size=row[2],
                confidence_interval=tuple(json.loads(row[3])),
                p_value=row[4],
                is_significant=bool(row[5]),
                winner=row[6]
            ))
        
        return results
    
    def get_model_statistics(self) -> Dict[str, Any]:
        """获取模型统计信息"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 任务指标统计
            cursor.execute('SELECT COUNT(*) FROM task_metrics')
            total_metrics = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM task_metrics WHERE success = 1')
            successful_metrics = cursor.fetchone()[0]
            
            # 预测统计
            cursor.execute('SELECT COUNT(*) FROM predictions')
            total_predictions = cursor.fetchone()[0]
            
            # 异常检测统计
            cursor.execute('SELECT COUNT(*) FROM anomalies WHERE is_anomaly = 1')
            total_anomalies = cursor.fetchone()[0]
            
            # A/B测试统计
            cursor.execute('SELECT COUNT(*) FROM ab_tests')
            total_ab_tests = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM ab_tests WHERE status = "active"')
            active_ab_tests = cursor.fetchone()[0]
        
        return {
            'total_metrics': total_metrics,
            'successful_metrics': successful_metrics,
            'success_rate': successful_metrics / total_metrics if total_metrics > 0 else 0,
            'total_predictions': total_predictions,
            'total_anomalies': total_anomalies,
            'total_ab_tests': total_ab_tests,
            'active_ab_tests': active_ab_tests,
            'models_available': len(self._models_cache),
            'last_updated': datetime.now().isoformat()
        }
    
    def save_models(self):
        """保存模型到文件"""
        if not JOBLIB_AVAILABLE:
            self.logger.warning("joblib不可用，无法保存模型")
            return
        
        try:
            with self._lock:
                for model_name, model in self._models_cache.items():
                    model_path = os.path.join(self.models_dir, f"{model_name}_model.pkl")
                    joblib.dump(model, model_path)
                
                for scaler_name, scaler in self._scaler_cache.items():
                    scaler_path = os.path.join(self.models_dir, f"{scaler_name}.pkl")
                    joblib.dump(scaler, scaler_path)
            
            self.logger.info("模型保存成功")
        except Exception as e:
            self.logger.error(f"保存模型失败: {e}")
    
    def load_models(self):
        """从文件加载模型"""
        if not JOBLIB_AVAILABLE:
            self.logger.warning("joblib不可用，无法加载模型")
            return
        
        try:
            with self._lock:
                # 加载预测模型
                duration_model_path = os.path.join(self.models_dir, "duration_model.pkl")
                if os.path.exists(duration_model_path):
                    self._models_cache['duration'] = joblib.load(duration_model_path)
                
                success_model_path = os.path.join(self.models_dir, "success_model.pkl")
                if os.path.exists(success_model_path):
                    self._models_cache['success'] = joblib.load(success_model_path)
                
                # 加载标准化器
                scaler_path = os.path.join(self.models_dir, "scaler.pkl")
                if os.path.exists(scaler_path):
                    self._scaler_cache['scaler'] = joblib.load(scaler_path)
            
            self.logger.info("模型加载成功")
        except Exception as e:
            self.logger.error(f"加载模型失败: {e}")
    
    def cleanup_old_data(self, days: int = 90):
        """清理旧数据"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 清理旧的任务指标
            cursor.execute('DELETE FROM task_metrics WHERE timestamp < ?', 
                         (cutoff_date.isoformat(),))
            metrics_deleted = cursor.rowcount
            
            # 清理旧的预测结果
            cursor.execute('DELETE FROM predictions WHERE created_at < ?', 
                         (cutoff_date.isoformat(),))
            predictions_deleted = cursor.rowcount
            
            # 清理旧的异常检测结果
            cursor.execute('DELETE FROM anomalies WHERE created_at < ?', 
                         (cutoff_date.isoformat(),))
            anomalies_deleted = cursor.rowcount
            
            conn.commit()
        
        self.logger.info(f"数据清理完成: 指标{metrics_deleted}条, 预测{predictions_deleted}条, 异常{anomalies_deleted}条")