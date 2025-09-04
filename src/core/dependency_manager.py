"""
任务依赖管理器 - 负责任务依赖关系管理和执行优化
"""

import logging
import threading
from typing import Dict, List, Set, Optional, Any, Callable
from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum
import time


class DependencyType(Enum):
    """依赖类型"""
    REQUIRED = "required"  # 必需依赖
    OPTIONAL = "optional"  # 可选依赖
    CONDITIONAL = "conditional"  # 条件依赖


@dataclass
class DependencyInfo:
    """依赖信息"""
    task_id: str
    dependency_type: DependencyType
    condition: Optional[Callable] = None
    timeout: Optional[int] = None
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class TaskNode:
    """任务节点"""
    task_id: str
    dependencies: List[DependencyInfo]
    dependents: List[str]
    status: str = "pending"
    priority: int = 1
    resource_requirements: Dict[str, Any] = None
    execution_time: Optional[float] = None
    last_execution: Optional[float] = None


class DependencyManager:
    """任务依赖管理器"""
    
    def __init__(self):
        """初始化依赖管理器"""
        self.logger = logging.getLogger(__name__)
        
        # 任务依赖图
        self.task_graph: Dict[str, TaskNode] = {}
        
        # 资源管理器
        self.resource_manager = ResourceManager()
        
        # 执行队列
        self.execution_queue = deque()
        
        # 线程锁
        self._lock = threading.Lock()
        
        # 执行状态
        self._executing_tasks: Set[str] = set()
        self._completed_tasks: Set[str] = set()
        self._failed_tasks: Set[str] = set()
        
        self.logger.debug("依赖管理器初始化完成")
    
    def add_task(self, task_id: str, dependencies: List[Dict[str, Any]] = None, 
                 priority: int = 1, resource_requirements: Dict[str, Any] = None) -> bool:
        """
        添加任务到依赖图
        
        Args:
            task_id: 任务ID
            dependencies: 依赖列表
            priority: 任务优先级
            resource_requirements: 资源需求
            
        Returns:
            是否添加成功
        """
        try:
            with self._lock:
                # 检查任务是否已存在
                if task_id in self.task_graph:
                    self.logger.warning(f"任务已存在: {task_id}")
                    return False
                
                # 解析依赖信息
                dependency_infos = []
                if dependencies:
                    for dep in dependencies:
                        dep_info = DependencyInfo(
                            task_id=dep['task_id'],
                            dependency_type=DependencyType(dep.get('type', 'required')),
                            condition=dep.get('condition'),
                            timeout=dep.get('timeout'),
                            max_retries=dep.get('max_retries', 3)
                        )
                        dependency_infos.append(dep_info)
                
                # 创建任务节点
                task_node = TaskNode(
                    task_id=task_id,
                    dependencies=dependency_infos,
                    dependents=[],
                    priority=priority,
                    resource_requirements=resource_requirements or {}
                )
                
                # 添加到依赖图
                self.task_graph[task_id] = task_node
                
                # 更新依赖关系
                self._update_dependency_relationships()
                
                self.logger.info(f"任务添加成功: {task_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"添加任务失败 {task_id}: {e}")
            return False
    
    def remove_task(self, task_id: str) -> bool:
        """
        从依赖图中移除任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否移除成功
        """
        try:
            with self._lock:
                if task_id not in self.task_graph:
                    return False
                
                # 移除任务节点
                del self.task_graph[task_id]
                
                # 更新依赖关系
                self._update_dependency_relationships()
                
                self.logger.info(f"任务移除成功: {task_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"移除任务失败 {task_id}: {e}")
            return False
    
    def _update_dependency_relationships(self):
        """更新依赖关系"""
        # 清空所有依赖关系
        for node in self.task_graph.values():
            node.dependents.clear()
        
        # 重新建立依赖关系
        for task_id, node in self.task_graph.items():
            for dep_info in node.dependencies:
                if dep_info.task_id in self.task_graph:
                    self.task_graph[dep_info.task_id].dependents.append(task_id)
    
    def check_circular_dependencies(self) -> List[List[str]]:
        """
        检查循环依赖
        
        Returns:
            循环依赖列表
        """
        try:
            visited = set()
            rec_stack = set()
            cycles = []
            
            def dfs(node_id: str, path: List[str]):
                if node_id in rec_stack:
                    # 发现循环依赖
                    cycle_start = path.index(node_id)
                    cycles.append(path[cycle_start:] + [node_id])
                    return
                
                if node_id in visited:
                    return
                
                visited.add(node_id)
                rec_stack.add(node_id)
                path.append(node_id)
                
                if node_id in self.task_graph:
                    for dep_info in self.task_graph[node_id].dependencies:
                        dfs(dep_info.task_id, path.copy())
                
                rec_stack.remove(node_id)
            
            # 对所有节点进行DFS
            for task_id in self.task_graph:
                if task_id not in visited:
                    dfs(task_id, [])
            
            return cycles
            
        except Exception as e:
            self.logger.error(f"检查循环依赖失败: {e}")
            return []
    
    def get_execution_order(self) -> List[List[str]]:
        """
        获取任务执行顺序（拓扑排序）
        
        Returns:
            分层执行顺序
        """
        try:
            # 检查循环依赖
            cycles = self.check_circular_dependencies()
            if cycles:
                self.logger.error(f"发现循环依赖: {cycles}")
                return []
            
            # 计算入度
            in_degree = defaultdict(int)
            for task_id, node in self.task_graph.items():
                in_degree[task_id] = len(node.dependencies)
            
            # 拓扑排序
            execution_layers = []
            queue = deque()
            
            # 添加入度为0的节点
            for task_id, degree in in_degree.items():
                if degree == 0:
                    queue.append(task_id)
            
            while queue:
                # 按优先级排序当前层的任务
                current_layer = sorted(queue, key=lambda x: self.task_graph[x].priority, reverse=True)
                execution_layers.append(current_layer)
                
                # 处理当前层的所有任务
                for task_id in current_layer:
                    queue.remove(task_id)
                    
                    # 更新依赖任务的入度
                    for dependent_id in self.task_graph[task_id].dependents:
                        in_degree[dependent_id] -= 1
                        if in_degree[dependent_id] == 0:
                            queue.append(dependent_id)
            
            # 检查是否所有任务都被处理
            if len([x for x in in_degree.values() if x > 0]) > 0:
                self.logger.error("存在无法执行的任务（依赖关系错误）")
                return []
            
            return execution_layers
            
        except Exception as e:
            self.logger.error(f"获取执行顺序失败: {e}")
            return []
    
    def can_execute_task(self, task_id: str) -> bool:
        """
        检查任务是否可以执行
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否可以执行
        """
        try:
            if task_id not in self.task_graph:
                return False
            
            node = self.task_graph[task_id]
            
            # 检查依赖是否满足
            for dep_info in node.dependencies:
                if not self._is_dependency_satisfied(dep_info):
                    return False
            
            # 检查资源是否可用
            if not self.resource_manager.can_allocate_resources(node.resource_requirements):
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"检查任务执行条件失败 {task_id}: {e}")
            return False
    
    def _is_dependency_satisfied(self, dep_info: DependencyInfo) -> bool:
        """
        检查依赖是否满足
        
        Args:
            dep_info: 依赖信息
            
        Returns:
            依赖是否满足
        """
        try:
            # 检查依赖任务是否完成
            if dep_info.task_id not in self._completed_tasks:
                return False
            
            # 检查条件依赖
            if dep_info.dependency_type == DependencyType.CONDITIONAL and dep_info.condition:
                try:
                    return dep_info.condition()
                except Exception as e:
                    self.logger.error(f"条件依赖检查失败: {e}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"检查依赖满足失败: {e}")
            return False
    
    def mark_task_completed(self, task_id: str, result: Dict[str, Any] = None):
        """
        标记任务完成
        
        Args:
            task_id: 任务ID
            result: 执行结果
        """
        try:
            with self._lock:
                if task_id in self.task_graph:
                    self.task_graph[task_id].status = "completed"
                    self.task_graph[task_id].last_execution = time.time()
                    
                    if result:
                        self.task_graph[task_id].execution_time = result.get('execution_time')
                
                self._completed_tasks.add(task_id)
                self._executing_tasks.discard(task_id)
                
                # 释放资源
                if task_id in self.task_graph:
                    self.resource_manager.release_resources(
                        self.task_graph[task_id].resource_requirements
                    )
                
                self.logger.info(f"任务标记完成: {task_id}")
                
        except Exception as e:
            self.logger.error(f"标记任务完成失败 {task_id}: {e}")
    
    def mark_task_failed(self, task_id: str, error: str = None):
        """
        标记任务失败
        
        Args:
            task_id: 任务ID
            error: 错误信息
        """
        try:
            with self._lock:
                if task_id in self.task_graph:
                    self.task_graph[task_id].status = "failed"
                
                self._failed_tasks.add(task_id)
                self._executing_tasks.discard(task_id)
                
                # 释放资源
                if task_id in self.task_graph:
                    self.resource_manager.release_resources(
                        self.task_graph[task_id].resource_requirements
                    )
                
                self.logger.error(f"任务标记失败: {task_id}, 错误: {error}")
                
        except Exception as e:
            self.logger.error(f"标记任务失败失败 {task_id}: {e}")
    
    def get_ready_tasks(self) -> List[str]:
        """
        获取可以执行的任务列表
        
        Returns:
            可执行任务列表
        """
        try:
            ready_tasks = []
            
            for task_id, node in self.task_graph.items():
                if (task_id not in self._executing_tasks and 
                    task_id not in self._completed_tasks and 
                    task_id not in self._failed_tasks and
                    self.can_execute_task(task_id)):
                    ready_tasks.append(task_id)
            
            # 按优先级排序
            ready_tasks.sort(key=lambda x: self.task_graph[x].priority, reverse=True)
            
            return ready_tasks
            
        except Exception as e:
            self.logger.error(f"获取可执行任务失败: {e}")
            return []
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务状态信息
        """
        try:
            if task_id not in self.task_graph:
                return {}
            
            node = self.task_graph[task_id]
            
            return {
                'task_id': task_id,
                'status': node.status,
                'priority': node.priority,
                'dependencies': [dep.task_id for dep in node.dependencies],
                'dependents': node.dependents,
                'execution_time': node.execution_time,
                'last_execution': node.last_execution,
                'resource_requirements': node.resource_requirements
            }
            
        except Exception as e:
            self.logger.error(f"获取任务状态失败 {task_id}: {e}")
            return {}
    
    def get_dependency_graph(self) -> Dict[str, Any]:
        """
        获取依赖图信息
        
        Returns:
            依赖图信息
        """
        try:
            return {
                'tasks': {task_id: self.get_task_status(task_id) 
                         for task_id in self.task_graph},
                'execution_order': self.get_execution_order(),
                'ready_tasks': self.get_ready_tasks(),
                'executing_tasks': list(self._executing_tasks),
                'completed_tasks': list(self._completed_tasks),
                'failed_tasks': list(self._failed_tasks)
            }
            
        except Exception as e:
            self.logger.error(f"获取依赖图失败: {e}")
            return {}
    
    def add_task_dependency(self, task_id: str, dependency_task_id: str, 
                           dependency_type: str = "required", condition: Callable = None) -> bool:
        """
        添加任务依赖
        
        Args:
            task_id: 任务ID
            dependency_task_id: 依赖任务ID
            dependency_type: 依赖类型
            condition: 条件函数
            
        Returns:
            是否添加成功
        """
        try:
            # 检查任务是否存在
            if task_id not in self.task_graph:
                self.logger.error(f"任务不存在: {task_id}")
                return False
            
            if dependency_task_id not in self.task_graph:
                self.logger.error(f"依赖任务不存在: {dependency_task_id}")
                return False
            
            # 创建依赖信息
            dep_info = DependencyInfo(
                task_id=dependency_task_id,
                dependency_type=DependencyType(dependency_type),
                condition=condition
            )
            
            # 添加到依赖图
            task_node = self.task_graph[task_id]
            task_node.dependencies.append(dep_info)
            
            # 更新依赖关系
            self._update_dependency_relationships()
            
            self.logger.info(f"依赖添加成功: {task_id} -> {dependency_task_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"添加任务依赖失败: {e}")
            return False


class ResourceManager:
    """资源管理器"""
    
    def __init__(self):
        """初始化资源管理器"""
        self.logger = logging.getLogger(__name__)
        
        # 可用资源
        self.available_resources = {
            'cpu': 100,  # CPU百分比
            'memory': 8192,  # 内存MB
            'disk': 100000,  # 磁盘MB
            'network': 1000,  # 网络MB/s
            'gpu': 1,  # GPU数量
        }
        
        # 已分配资源
        self.allocated_resources = defaultdict(lambda: defaultdict(int))
        
        # 资源锁
        self._lock = threading.Lock()
        
        self.logger.debug("资源管理器初始化完成")
    
    def can_allocate_resources(self, requirements: Dict[str, Any]) -> bool:
        """
        检查是否可以分配资源
        
        Args:
            requirements: 资源需求
            
        Returns:
            是否可以分配
        """
        try:
            with self._lock:
                for resource_type, amount in requirements.items():
                    if resource_type not in self.available_resources:
                        continue
                    
                    available = self.available_resources[resource_type]
                    allocated = sum(self.allocated_resources[resource_type].values())
                    
                    if available - allocated < amount:
                        return False
                
                return True
                
        except Exception as e:
            self.logger.error(f"检查资源分配失败: {e}")
            return False
    
    def allocate_resources(self, task_id: str, requirements: Dict[str, Any]) -> bool:
        """
        分配资源
        
        Args:
            task_id: 任务ID
            requirements: 资源需求
            
        Returns:
            是否分配成功
        """
        try:
            with self._lock:
                if not self.can_allocate_resources(requirements):
                    return False
                
                for resource_type, amount in requirements.items():
                    if resource_type in self.available_resources:
                        self.allocated_resources[resource_type][task_id] = amount
                
                self.logger.info(f"资源分配成功: {task_id}, 需求: {requirements}")
                return True
                
        except Exception as e:
            self.logger.error(f"分配资源失败 {task_id}: {e}")
            return False
    
    def release_resources(self, requirements: Dict[str, Any]):
        """
        释放资源
        
        Args:
            requirements: 要释放的资源
        """
        try:
            with self._lock:
                for resource_type, amount in requirements.items():
                    if resource_type in self.allocated_resources:
                        # 找到对应的任务并释放资源
                        for task_id, allocated_amount in list(self.allocated_resources[resource_type].items()):
                            if allocated_amount >= amount:
                                self.allocated_resources[resource_type][task_id] -= amount
                                if self.allocated_resources[resource_type][task_id] <= 0:
                                    del self.allocated_resources[resource_type][task_id]
                                break
                
                self.logger.debug(f"资源释放完成: {requirements}")
                
        except Exception as e:
            self.logger.error(f"释放资源失败: {e}")
    
    def get_resource_status(self) -> Dict[str, Any]:
        """
        获取资源状态
        
        Returns:
            资源状态信息
        """
        try:
            with self._lock:
                status = {}
                for resource_type, total in self.available_resources.items():
                    allocated = sum(self.allocated_resources[resource_type].values())
                    status[resource_type] = {
                        'total': total,
                        'allocated': allocated,
                        'available': total - allocated,
                        'utilization': (allocated / total * 100) if total > 0 else 0
                    }
                
                return status
                
        except Exception as e:
            self.logger.error(f"获取资源状态失败: {e}")
            return {}
