"""
AI模型管理服务
提供模型版本控制、自动模型切换、模型微调等功能
"""

import os
import json
import hashlib
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import pymysql
from pathlib import Path

from .ai_service import AIService


class ModelStatus(Enum):
    """模型状态枚举"""
    ACTIVE = "active"           # 活跃状态
    INACTIVE = "inactive"       # 非活跃状态
    DEPRECATED = "deprecated"   # 已废弃
    TESTING = "testing"         # 测试中
    TRAINING = "training"       # 训练中


class ModelType(Enum):
    """模型类型枚举"""
    TEXT_GENERATION = "text_generation"     # 文本生成
    CODE_GENERATION = "code_generation"     # 代码生成
    TEXT_ANALYSIS = "text_analysis"         # 文本分析
    MULTIMODAL = "multimodal"               # 多模态
    EMBEDDING = "embedding"                  # 嵌入模型


@dataclass
class ModelVersion:
    """模型版本信息"""
    version_id: str
    model_name: str
    model_type: ModelType
    version: str
    provider: str
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    parameters: Dict[str, Any] = None
    performance_metrics: Dict[str, float] = None
    created_at: datetime = None
    updated_at: datetime = None
    status: ModelStatus = ModelStatus.INACTIVE
    usage_count: int = 0
    success_rate: float = 0.0
    avg_response_time: float = 0.0
    cost_per_request: float = 0.0
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}
        if self.performance_metrics is None:
            self.performance_metrics = {}
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()


@dataclass
class ModelPerformance:
    """模型性能指标"""
    model_version_id: str
    timestamp: datetime
    response_time: float
    success: bool
    cost: float
    tokens_used: int
    error_message: Optional[str] = None


class AIModelManager:
    """AI模型管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # MySQL数据库配置
        self.db_config = config.get('database', {})
        self.host = self.db_config.get('host', 'localhost')
        self.port = self.db_config.get('port', 3306)
        self.user = self.db_config.get('user', 'root')
        self.password = self.db_config.get('password', '')
        self.database = self.db_config.get('database', 'auto_coder')
        self.charset = self.db_config.get('charset', 'utf8mb4')
        
        self.models_dir = config.get('models_directory', './models')
        self.performance_history_size = config.get('performance_history_size', 1000)
        self.auto_switch_threshold = config.get('auto_switch_threshold', 0.8)
        self.performance_window = config.get('performance_window_hours', 24)
        
        # 确保目录存在
        os.makedirs(self.models_dir, exist_ok=True)
        
        # 初始化数据库
        self._init_database()
        
        # 模型缓存
        self._model_cache: Dict[str, ModelVersion] = {}
        self._active_models: Dict[ModelType, ModelVersion] = {}
        self._cache_lock = threading.Lock()
        
        # 性能监控
        self._performance_data: List[ModelPerformance] = []
        self._performance_lock = threading.Lock()
        
        # 加载现有模型
        self._load_models()
        
        self.logger.info("AI模型管理器初始化完成")
    
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
            
            # 创建模型版本表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS model_versions (
                    version_id VARCHAR(255) PRIMARY KEY,
                    model_name VARCHAR(255) NOT NULL,
                    model_type VARCHAR(100) NOT NULL,
                    version VARCHAR(100) NOT NULL,
                    provider VARCHAR(100) NOT NULL,
                    api_key TEXT,
                    endpoint TEXT,
                    parameters TEXT,
                    performance_metrics TEXT,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    status VARCHAR(50) NOT NULL,
                    usage_count INT DEFAULT 0,
                    success_rate DECIMAL(5,4) DEFAULT 0.0,
                    avg_response_time DECIMAL(10,3) DEFAULT 0.0,
                    cost_per_request DECIMAL(10,6) DEFAULT 0.0,
                    INDEX idx_model_type (model_type),
                    INDEX idx_status (status)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            ''')
            
            # 创建性能历史表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS model_performance (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    model_version_id VARCHAR(255) NOT NULL,
                    timestamp DATETIME NOT NULL,
                    response_time DECIMAL(10,3) NOT NULL,
                    success TINYINT NOT NULL,
                    cost DECIMAL(10,6) NOT NULL,
                    tokens_used INT NOT NULL,
                    error_message TEXT,
                    INDEX idx_model_version_id (model_version_id),
                    INDEX idx_timestamp (timestamp),
                    FOREIGN KEY (model_version_id) REFERENCES model_versions (version_id) ON DELETE CASCADE
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
    
    def _load_models(self):
        """从数据库加载模型"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM model_versions')
            rows = cursor.fetchall()
            
            for row in rows:
                model_version = self._row_to_model_version(row)
                self._model_cache[model_version.version_id] = model_version
                
                if model_version.status == ModelStatus.ACTIVE:
                    self._active_models[model_version.model_type] = model_version
        
        self.logger.info(f"加载了 {len(self._model_cache)} 个模型版本")
    
    def _row_to_model_version(self, row) -> ModelVersion:
        """将数据库行转换为ModelVersion对象"""
        return ModelVersion(
            version_id=row[0],
            model_name=row[1],
            model_type=ModelType(row[2]),
            version=row[3],
            provider=row[4],
            api_key=row[5],
            endpoint=row[6],
            parameters=json.loads(row[7]) if row[7] else {},
            performance_metrics=json.loads(row[8]) if row[8] else {},
            created_at=row[9] if isinstance(row[9], datetime) else datetime.fromisoformat(row[9]),
            updated_at=row[10] if isinstance(row[10], datetime) else datetime.fromisoformat(row[10]),
            status=ModelStatus(row[11]),
            usage_count=row[12],
            success_rate=float(row[13]),
            avg_response_time=float(row[14]),
            cost_per_request=float(row[15])
        )
    
    def _model_version_to_row(self, model_version: ModelVersion) -> tuple:
        """将ModelVersion对象转换为数据库行"""
        return (
            model_version.version_id,
            model_version.model_name,
            model_version.model_type.value,
            model_version.version,
            model_version.provider,
            model_version.api_key,
            model_version.endpoint,
            json.dumps(model_version.parameters),
            json.dumps(model_version.performance_metrics),
            model_version.created_at,
            model_version.updated_at,
            model_version.status.value,
            model_version.usage_count,
            model_version.success_rate,
            model_version.avg_response_time,
            model_version.cost_per_request
        )
    
    def register_model(self, model_name: str, model_type: ModelType, version: str, 
                      provider: str, api_key: Optional[str] = None, 
                      endpoint: Optional[str] = None, parameters: Dict[str, Any] = None) -> str:
        """
        注册新模型版本
        
        Args:
            model_name: 模型名称
            model_type: 模型类型
            version: 版本号
            provider: 提供商
            api_key: API密钥
            endpoint: 端点URL
            parameters: 模型参数
            
        Returns:
            模型版本ID
        """
        # 生成版本ID
        version_id = self._generate_version_id(model_name, version, provider)
        
        # 检查是否已存在
        if version_id in self._model_cache:
            raise ValueError(f"模型版本 {version_id} 已存在")
        
        # 创建模型版本
        model_version = ModelVersion(
            version_id=version_id,
            model_name=model_name,
            model_type=model_type,
            version=version,
            provider=provider,
            api_key=api_key,
            endpoint=endpoint,
            parameters=parameters or {}
        )
        
        # 保存到数据库
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO model_versions VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', self._model_version_to_row(model_version))
        
        # 添加到缓存
        with self._cache_lock:
            self._model_cache[version_id] = model_version
        
        self.logger.info(f"注册新模型版本: {version_id}")
        return version_id
    
    def _generate_version_id(self, model_name: str, version: str, provider: str) -> str:
        """生成模型版本ID"""
        content = f"{model_name}:{version}:{provider}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def get_model_version(self, version_id: str) -> Optional[ModelVersion]:
        """获取模型版本"""
        return self._model_cache.get(version_id)
    
    def get_active_model(self, model_type: ModelType) -> Optional[ModelVersion]:
        """获取活跃模型"""
        return self._active_models.get(model_type)
    
    def set_active_model(self, version_id: str) -> bool:
        """
        设置活跃模型
        
        Args:
            version_id: 模型版本ID
            
        Returns:
            是否设置成功
        """
        model_version = self._model_cache.get(version_id)
        if not model_version:
            self.logger.error(f"模型版本 {version_id} 不存在")
            return False
        
        # 更新数据库
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 将同类型的所有模型设为非活跃
            cursor.execute('''
                UPDATE model_versions 
                SET status = %s, updated_at = %s 
                WHERE model_type = %s
            ''', (ModelStatus.INACTIVE.value, datetime.now(), model_version.model_type.value))
            
            # 设置指定模型为活跃
            cursor.execute('''
                UPDATE model_versions 
                SET status = %s, updated_at = %s 
                WHERE version_id = %s
            ''', (ModelStatus.ACTIVE.value, datetime.now(), version_id))
        
        # 更新缓存
        with self._cache_lock:
            # 更新所有同类型模型状态
            for mv in self._model_cache.values():
                if mv.model_type == model_version.model_type:
                    mv.status = ModelStatus.INACTIVE
                    mv.updated_at = datetime.now()
            
            # 设置活跃模型
            model_version.status = ModelStatus.ACTIVE
            model_version.updated_at = datetime.now()
            self._active_models[model_version.model_type] = model_version
        
        self.logger.info(f"设置活跃模型: {version_id}")
        return True
    
    def list_models(self, model_type: Optional[ModelType] = None, 
                   status: Optional[ModelStatus] = None) -> List[ModelVersion]:
        """
        列出模型版本
        
        Args:
            model_type: 模型类型过滤
            status: 状态过滤
            
        Returns:
            模型版本列表
        """
        models = []
        
        for model_version in self._model_cache.values():
            if model_type and model_version.model_type != model_type:
                continue
            if status and model_version.status != status:
                continue
            models.append(model_version)
        
        # 按创建时间排序
        models.sort(key=lambda x: x.created_at, reverse=True)
        return models
    
    def update_model_performance(self, version_id: str, response_time: float, 
                               success: bool, cost: float, tokens_used: int, 
                               error_message: Optional[str] = None):
        """
        更新模型性能指标
        
        Args:
            version_id: 模型版本ID
            response_time: 响应时间
            success: 是否成功
            cost: 成本
            tokens_used: 使用的token数
            error_message: 错误信息
        """
        model_version = self._model_cache.get(version_id)
        if not model_version:
            self.logger.warning(f"模型版本 {version_id} 不存在，无法更新性能")
            return
        
        # 创建性能记录
        performance = ModelPerformance(
            model_version_id=version_id,
            timestamp=datetime.now(),
            response_time=response_time,
            success=success,
            cost=cost,
            tokens_used=tokens_used,
            error_message=error_message
        )
        
        # 保存到数据库
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO model_performance 
                (model_version_id, timestamp, response_time, success, cost, tokens_used, error_message)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (
                version_id,
                performance.timestamp,
                response_time,
                1 if success else 0,
                cost,
                tokens_used,
                error_message
            ))
            
            # 更新模型统计信息
            self._update_model_statistics(cursor, model_version, performance)
        
        # 更新缓存
        with self._cache_lock:
            model_version.usage_count += 1
            model_version.updated_at = datetime.now()
        
        # 添加到性能历史
        with self._performance_lock:
            self._performance_data.append(performance)
            
            # 清理旧数据
            cutoff_time = datetime.now() - timedelta(hours=self.performance_window)
            self._performance_data = [
                p for p in self._performance_data 
                if p.timestamp > cutoff_time
            ]
        
        # 检查是否需要自动切换模型
        self._check_auto_switch(model_version.model_type)
    
    def _update_model_statistics(self, cursor, model_version: ModelVersion, 
                                performance: ModelPerformance):
        """更新模型统计信息"""
        # 获取最近的性能数据
        cursor.execute('''
            SELECT response_time, success, cost 
            FROM model_performance 
            WHERE model_version_id = %s 
            ORDER BY timestamp DESC 
            LIMIT 100
        ''', (model_version.version_id,))
        
        recent_performance = cursor.fetchall()
        
        if recent_performance:
            response_times = [p[0] for p in recent_performance]
            success_count = sum(1 for p in recent_performance if p[1])
            costs = [p[2] for p in recent_performance]
            
            avg_response_time = sum(response_times) / len(response_times)
            success_rate = success_count / len(recent_performance)
            avg_cost = sum(costs) / len(costs)
            
            # 更新数据库
            cursor.execute('''
                UPDATE model_versions 
                SET success_rate = %s, avg_response_time = %s, cost_per_request = %s, updated_at = %s
                WHERE version_id = %s
            ''', (success_rate, avg_response_time, avg_cost, 
                  datetime.now(), model_version.version_id))
            
            # 更新缓存
            model_version.success_rate = success_rate
            model_version.avg_response_time = avg_response_time
            model_version.cost_per_request = avg_cost
    
    def _check_auto_switch(self, model_type: ModelType):
        """检查是否需要自动切换模型"""
        if not self.config.get('auto_switch_enabled', True):
            return
        
        active_model = self._active_models.get(model_type)
        if not active_model:
            return
        
        # 检查性能是否低于阈值
        if active_model.success_rate < self.auto_switch_threshold:
            self.logger.warning(f"活跃模型 {active_model.version_id} 成功率过低: {active_model.success_rate}")
            
            # 寻找更好的模型
            better_model = self._find_better_model(model_type, active_model)
            if better_model:
                self.logger.info(f"自动切换到更好的模型: {better_model.version_id}")
                self.set_active_model(better_model.version_id)
    
    def _find_better_model(self, model_type: ModelType, current_model: ModelVersion) -> Optional[ModelVersion]:
        """寻找更好的模型"""
        candidates = []
        
        for model_version in self._model_cache.values():
            if (model_version.model_type == model_type and 
                model_version.status != ModelStatus.DEPRECATED and
                model_version.version_id != current_model.version_id):
                candidates.append(model_version)
        
        if not candidates:
            return None
        
        # 按成功率排序
        candidates.sort(key=lambda x: x.success_rate, reverse=True)
        
        # 返回成功率最高的模型
        best_candidate = candidates[0]
        if best_candidate.success_rate > current_model.success_rate:
            return best_candidate
        
        return None
    
    def get_model_performance_history(self, version_id: str, 
                                    hours: int = 24) -> List[ModelPerformance]:
        """
        获取模型性能历史
        
        Args:
            version_id: 模型版本ID
            hours: 查询小时数
            
        Returns:
            性能历史列表
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT model_version_id, timestamp, response_time, success, cost, tokens_used, error_message
                FROM model_performance 
                WHERE model_version_id = %s AND timestamp > %s
                ORDER BY timestamp DESC
            ''', (version_id, cutoff_time))
            
            rows = cursor.fetchall()
            
            performance_list = []
            for row in rows:
                performance = ModelPerformance(
                    model_version_id=row[0],
                    timestamp=row[1] if isinstance(row[1], datetime) else datetime.fromisoformat(row[1]),
                    response_time=row[2],
                    success=bool(row[3]),
                    cost=row[4],
                    tokens_used=row[5],
                    error_message=row[6]
                )
                performance_list.append(performance)
            
            return performance_list
    
    def delete_model_version(self, version_id: str) -> bool:
        """
        删除模型版本
        
        Args:
            version_id: 模型版本ID
            
        Returns:
            是否删除成功
        """
        model_version = self._model_cache.get(version_id)
        if not model_version:
            return False
        
        # 检查是否为活跃模型
        if model_version.status == ModelStatus.ACTIVE:
            self.logger.error(f"无法删除活跃模型: {version_id}")
            return False
        
        # 从数据库删除
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 删除性能历史
            cursor.execute('DELETE FROM model_performance WHERE model_version_id = %s', (version_id,))
            
            # 删除模型版本
            cursor.execute('DELETE FROM model_versions WHERE version_id = %s', (version_id,))
        
        # 从缓存删除
        with self._cache_lock:
            if version_id in self._model_cache:
                del self._model_cache[version_id]
        
        self.logger.info(f"删除模型版本: {version_id}")
        return True
    
    def get_model_statistics(self) -> Dict[str, Any]:
        """获取模型统计信息"""
        stats = {
            'total_models': len(self._model_cache),
            'active_models': len(self._active_models),
            'model_types': {},
            'performance_summary': {}
        }
        
        # 按类型统计
        for model_type in ModelType:
            type_models = [mv for mv in self._model_cache.values() if mv.model_type == model_type]
            stats['model_types'][model_type.value] = {
                'count': len(type_models),
                'active': len([mv for mv in type_models if mv.status == ModelStatus.ACTIVE]),
                'avg_success_rate': sum(mv.success_rate for mv in type_models) / len(type_models) if type_models else 0,
                'avg_response_time': sum(mv.avg_response_time for mv in type_models) / len(type_models) if type_models else 0
            }
        
        # 性能摘要
        if self._performance_data:
            recent_performance = [
                p for p in self._performance_data 
                if p.timestamp > datetime.now() - timedelta(hours=1)
            ]
            
            if recent_performance:
                stats['performance_summary'] = {
                    'recent_requests': len(recent_performance),
                    'avg_response_time': sum(p.response_time for p in recent_performance) / len(recent_performance),
                    'success_rate': sum(1 for p in recent_performance if p.success) / len(recent_performance),
                    'total_cost': sum(p.cost for p in recent_performance)
                }
        
        return stats
    
    def export_model_config(self, version_id: str) -> Dict[str, Any]:
        """
        导出模型配置
        
        Args:
            version_id: 模型版本ID
            
        Returns:
            模型配置字典
        """
        model_version = self._model_cache.get(version_id)
        if not model_version:
            raise ValueError(f"模型版本 {version_id} 不存在")
        
        config = asdict(model_version)
        config['model_type'] = model_version.model_type.value
        config['status'] = model_version.status.value
        config['created_at'] = model_version.created_at.isoformat()
        config['updated_at'] = model_version.updated_at.isoformat()
        
        return config
    
    def import_model_config(self, config: Dict[str, Any]) -> str:
        """
        导入模型配置
        
        Args:
            config: 模型配置字典
            
        Returns:
            模型版本ID
        """
        # 验证必要字段
        required_fields = ['model_name', 'model_type', 'version', 'provider']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"缺少必要字段: {field}")
        
        # 转换枚举类型
        config['model_type'] = ModelType(config['model_type'])
        if 'status' in config:
            config['status'] = ModelStatus(config['status'])
        
        # 转换时间字段
        if 'created_at' in config:
            config['created_at'] = datetime.fromisoformat(config['created_at'])
        if 'updated_at' in config:
            config['updated_at'] = datetime.fromisoformat(config['updated_at'])
        
        # 注册模型
        return self.register_model(
            model_name=config['model_name'],
            model_type=config['model_type'],
            version=config['version'],
            provider=config['provider'],
            api_key=config.get('api_key'),
            endpoint=config.get('endpoint'),
            parameters=config.get('parameters', {})
        )
