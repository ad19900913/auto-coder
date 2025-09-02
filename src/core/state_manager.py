"""
状态管理器 - 管理任务状态和状态文件
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"           # 等待执行
    RUNNING = "running"           # 正在执行
    COMPLETED = "completed"       # 执行完成
    FAILED = "failed"             # 执行失败
    CANCELLED = "cancelled"       # 已取消
    REVIEW_REQUIRED = "review_required"  # 需要审查
    REVIEWING = "reviewing"       # 正在审查
    APPROVED = "approved"         # 审查通过
    REJECTED = "rejected"         # 审查拒绝


class StateManager:
    """状态协调器，管理任务状态和状态文件"""
    
    def __init__(self, work_dir: str = "./states", config_manager=None):
        """
        初始化状态管理器
        
        Args:
            work_dir: 工作目录路径
            config_manager: 配置管理器实例
        """
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        
        # 状态文件锁
        self._state_locks = {}
    
    def create_state_file(self, task_id: str, task_type: str, 
                         initial_data: Dict[str, Any] = None) -> str:
        """
        创建状态文件
        
        Args:
            task_id: 任务ID
            task_type: 任务类型
            initial_data: 初始数据
            
        Returns:
            状态文件路径
        """
        state_file_path = self.work_dir / f"{task_id}.json"
        
        # 基础状态数据
        state_data = {
            'task_id': task_id,
            'task_type': task_type,
            'status': TaskStatus.PENDING.value,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'attempts': 0,
            'max_attempts': 3,
            'error_count': 0,
            'last_error': None,
            'progress': 0.0,
            'metadata': {},
            'history': []
        }
        
        # 合并初始数据
        if initial_data:
            state_data.update(initial_data)
        
        # 写入状态文件
        try:
            with open(state_file_path, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"状态文件创建成功: {state_file_path}")
            return str(state_file_path)
        except Exception as e:
            self.logger.error(f"状态文件创建失败: {e}")
            raise
    
    def load_state_file(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        加载状态文件
        
        Args:
            task_id: 任务ID
            
        Returns:
            状态数据字典，如果文件不存在则返回None
        """
        state_file_path = self.work_dir / f"{task_id}.json"
        
        if not state_file_path.exists():
            return None
        
        try:
            with open(state_file_path, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
            
            return state_data
        except Exception as e:
            self.logger.error(f"状态文件加载失败 {task_id}: {e}")
            return None
    
    def update_state(self, task_id: str, updates: Dict[str, Any], 
                    add_to_history: bool = True) -> bool:
        """
        更新任务状态
        
        Args:
            task_id: 任务ID
            updates: 要更新的字段
            add_to_history: 是否添加到历史记录
            
        Returns:
            更新是否成功
        """
        state_file_path = self.work_dir / f"{task_id}.json"
        
        if not state_file_path.exists():
            self.logger.warning(f"状态文件不存在: {task_id}")
            return False
        
        try:
            # 加载当前状态
            with open(state_file_path, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
            
            # 记录历史
            if add_to_history:
                history_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'previous_status': state_data.get('status'),
                    'updates': updates.copy()
                }
                state_data.setdefault('history', []).append(history_entry)
            
            # 更新状态
            state_data.update(updates)
            state_data['updated_at'] = datetime.now().isoformat()
            
            # 写入状态文件
            with open(state_file_path, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"状态更新成功: {task_id} -> {updates.get('status', '其他字段')}")
            return True
            
        except Exception as e:
            self.logger.error(f"状态更新失败 {task_id}: {e}")
            return False
    
    def update_task_status(self, task_id: str, status: TaskStatus, 
                          message: str = None, metadata: Dict[str, Any] = None,
                          progress: float = None) -> bool:
        """
        更新任务状态（兼容性方法）
        
        Args:
            task_id: 任务ID
            status: 新状态
            message: 状态消息
            metadata: 元数据
            progress: 进度值（0.0-1.0）
            
        Returns:
            更新是否成功
        """
        updates = {'status': status.value}
        
        if message:
            updates['last_message'] = message
        
        if progress is not None:
            updates['progress'] = max(0.0, min(1.0, progress))
        
        if metadata:
            updates['metadata'] = updates.get('metadata', {})
            updates['metadata'].update(metadata)
        
        return self.update_state(task_id, updates)
    
    def update_status(self, task_id: str, status: TaskStatus, 
                     message: str = None, metadata: Dict[str, Any] = None) -> bool:
        """
        更新任务状态
        
        Args:
            task_id: 任务ID
            status: 新状态
            message: 状态消息
            metadata: 元数据
            
        Returns:
            更新是否成功
        """
        updates = {'status': status.value}
        
        if message:
            updates['last_message'] = message
        
        if metadata:
            updates['metadata'] = updates.get('metadata', {})
            updates['metadata'].update(metadata)
        
        return self.update_state(task_id, updates)
    
    def increment_attempts(self, task_id: str) -> bool:
        """
        增加尝试次数
        
        Args:
            task_id: 任务ID
            
        Returns:
            更新是否成功
        """
        state_data = self.load_state_file(task_id)
        if not state_data:
            return False
        
        current_attempts = state_data.get('attempts', 0)
        return self.update_state(task_id, {'attempts': current_attempts + 1})
    
    def increment_task_errors(self, task_id: str, error_message: str) -> bool:
        """
        增加任务错误次数（兼容性方法）
        
        Args:
            task_id: 任务ID
            error_message: 错误消息
            
        Returns:
            更新是否成功
        """
        return self.increment_error_count(task_id, error_message)
    
    def increment_error_count(self, task_id: str, error_message: str) -> bool:
        """
        增加错误次数
        
        Args:
            task_id: 任务ID
            error_message: 错误消息
            
        Returns:
            更新是否成功
        """
        state_data = self.load_state_file(task_id)
        if not state_data:
            return False
        
        current_errors = state_data.get('error_count', 0)
        updates = {
            'error_count': current_errors + 1,
            'last_error': error_message,
            'last_error_at': datetime.now().isoformat()
        }
        
        return self.update_state(task_id, updates)
    
    def update_task_progress(self, task_id: str, progress: float, message: str = None) -> bool:
        """
        更新任务进度（兼容性方法）
        
        Args:
            task_id: 任务ID
            progress: 进度值（0.0-1.0）
            message: 进度消息
            
        Returns:
            更新是否成功
        """
        return self.set_progress(task_id, progress, message)
    
    def set_progress(self, task_id: str, progress: float, 
                    message: str = None) -> bool:
        """
        设置任务进度
        
        Args:
            task_id: 任务ID
            progress: 进度值（0.0-1.0）
            message: 进度消息
            
        Returns:
            更新是否成功
        """
        updates = {'progress': max(0.0, min(1.0, progress))}
        
        if message:
            updates['progress_message'] = message
        
        return self.update_state(task_id, updates)
    
    def add_metadata(self, task_id: str, key: str, value: Any) -> bool:
        """
        添加元数据
        
        Args:
            task_id: 任务ID
            key: 键名
            value: 值
            
        Returns:
            更新是否成功
        """
        state_data = self.load_state_file(task_id)
        if not state_data:
            return False
        
        metadata = state_data.get('metadata', {})
        metadata[key] = value
        
        return self.update_state(task_id, {'metadata': metadata})
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """
        获取任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务状态枚举值
        """
        state_data = self.load_state_file(task_id)
        if not state_data:
            return None
        
        try:
            return TaskStatus(state_data.get('status', 'unknown'))
        except ValueError:
            return None
    
    def is_task_running(self, task_id: str) -> bool:
        """
        检查任务是否正在运行
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否正在运行
        """
        status = self.get_task_status(task_id)
        return status in [TaskStatus.RUNNING, TaskStatus.REVIEWING]
    
    def can_retry(self, task_id: str) -> bool:
        """
        检查任务是否可以重试
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否可以重试
        """
        state_data = self.load_state_file(task_id)
        if not state_data:
            return False
        
        current_attempts = state_data.get('attempts', 0)
        max_attempts = state_data.get('max_attempts', 3)
        
        return current_attempts < max_attempts
    
    def get_running_tasks(self) -> List[str]:
        """
        获取所有正在运行的任务ID列表
        
        Returns:
            正在运行的任务ID列表
        """
        running_tasks = []
        
        for state_file in self.work_dir.glob("*.json"):
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    state_data = json.load(f)
                
                if state_data.get('status') in ['running', 'reviewing']:
                    running_tasks.append(state_data.get('task_id'))
            except Exception as e:
                self.logger.warning(f"读取状态文件失败 {state_file}: {e}")
        
        return running_tasks
    
    def get_task_summary(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取任务摘要信息
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务摘要字典
        """
        state_data = self.load_state_file(task_id)
        if not state_data:
            return None
        
        return {
            'task_id': state_data.get('task_id'),
            'task_type': state_data.get('task_type'),
            'status': state_data.get('status'),
            'progress': state_data.get('progress', 0.0),
            'attempts': state_data.get('attempts', 0),
            'error_count': state_data.get('error_count', 0),
            'created_at': state_data.get('created_at'),
            'updated_at': state_data.get('updated_at'),
            'last_error': state_data.get('last_error'),
            'metadata': state_data.get('metadata', {})
        }
    
    def cleanup_expired_states(self) -> int:
        """
        清理过期的状态文件（占位符方法）
        
        Returns:
            清理的文件数量
        """
        # 这个方法将由StateFileManager实现
        self.logger.info("状态文件清理功能由StateFileManager实现")
        return 0
    
    def delete_state_file(self, task_id: str) -> bool:
        """
        删除状态文件
        
        Args:
            task_id: 任务ID
            
        Returns:
            删除是否成功
        """
        state_file_path = self.work_dir / f"{task_id}.json"
        
        if not state_file_path.exists():
            return True
        
        try:
            state_file_path.unlink()
            self.logger.info(f"状态文件删除成功: {task_id}")
            return True
        except Exception as e:
            self.logger.error(f"状态文件删除失败 {task_id}: {e}")
            return False
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """
        获取所有任务的摘要信息
        
        Returns:
            任务摘要列表
        """
        tasks = []
        
        for state_file in self.work_dir.glob("*.json"):
            try:
                task_id = state_file.stem
                summary = self.get_task_summary(task_id)
                if summary:
                    tasks.append(summary)
            except Exception as e:
                self.logger.warning(f"获取任务摘要失败 {state_file}: {e}")
        
        # 按更新时间排序
        tasks.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
        
        return tasks
