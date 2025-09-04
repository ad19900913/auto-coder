"""
依赖管理功能测试
"""

import unittest
import time
from unittest.mock import Mock, patch
from typing import Dict, Any

from src.core.dependency_manager import (
    DependencyManager, DependencyType, ResourceManager,
    DependencyInfo, TaskNode
)


class TestDependencyManager(unittest.TestCase):
    """依赖管理器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.dependency_manager = DependencyManager()
    
    def test_add_task(self):
        """测试添加任务"""
        # 添加任务
        result = self.dependency_manager.add_task(
            task_id="test_task",
            dependencies=[],
            priority=1,
            resource_requirements={"cpu": 10, "memory": 512}
        )
        
        self.assertTrue(result)
        self.assertIn("test_task", self.dependency_manager.task_graph)
        
        # 测试重复添加
        result = self.dependency_manager.add_task("test_task")
        self.assertFalse(result)
    
    def test_dependency_relationships(self):
        """测试依赖关系"""
        # 添加依赖任务
        self.dependency_manager.add_task("task_a")
        self.dependency_manager.add_task("task_b")
        
        # 添加依赖关系
        self.dependency_manager.add_task(
            "task_c",
            dependencies=[
                {"task_id": "task_a", "type": "required"},
                {"task_id": "task_b", "type": "optional"}
            ]
        )
        
        # 验证依赖关系
        task_c = self.dependency_manager.task_graph["task_c"]
        self.assertEqual(len(task_c.dependencies), 2)
        self.assertEqual(task_c.dependencies[0].task_id, "task_a")
        self.assertEqual(task_c.dependencies[1].task_id, "task_b")
        
        # 验证反向依赖
        task_a = self.dependency_manager.task_graph["task_a"]
        self.assertIn("task_c", task_a.dependents)
    
    def test_circular_dependency_detection(self):
        """测试循环依赖检测"""
        # 创建循环依赖
        self.dependency_manager.add_task("task_1")
        self.dependency_manager.add_task("task_2")
        self.dependency_manager.add_task("task_3")
        
        # 添加循环依赖
        self.dependency_manager.add_task_dependency("task_1", "task_2")
        self.dependency_manager.add_task_dependency("task_2", "task_3")
        self.dependency_manager.add_task_dependency("task_3", "task_1")
        
        # 检测循环依赖
        cycles = self.dependency_manager.check_circular_dependencies()
        self.assertTrue(len(cycles) > 0)
        self.assertIn("task_1", cycles[0])
        self.assertIn("task_2", cycles[0])
        self.assertIn("task_3", cycles[0])
    
    def test_execution_order(self):
        """测试执行顺序"""
        # 创建任务链
        self.dependency_manager.add_task("task_1", priority=1)
        self.dependency_manager.add_task("task_2", priority=2)
        self.dependency_manager.add_task("task_3", priority=3)
        
        # 添加依赖关系
        self.dependency_manager.add_task_dependency("task_2", "task_1")
        self.dependency_manager.add_task_dependency("task_3", "task_2")
        
        # 获取执行顺序
        execution_order = self.dependency_manager.get_execution_order()
        
        # 验证执行顺序
        self.assertEqual(len(execution_order), 3)  # 3个层级
        self.assertIn("task_1", execution_order[0])  # 第一层
        self.assertIn("task_2", execution_order[1])  # 第二层
        self.assertIn("task_3", execution_order[2])  # 第三层
    
    def test_task_execution_conditions(self):
        """测试任务执行条件"""
        # 添加任务
        self.dependency_manager.add_task("task_a")
        self.dependency_manager.add_task(
            "task_b",
            dependencies=[{"task_id": "task_a", "type": "required"}]
        )
        
        # 任务a未完成时，任务b不能执行
        self.assertFalse(self.dependency_manager.can_execute_task("task_b"))
        
        # 标记任务a完成
        self.dependency_manager.mark_task_completed("task_a")
        
        # 现在任务b可以执行
        self.assertTrue(self.dependency_manager.can_execute_task("task_b"))
    
    def test_conditional_dependencies(self):
        """测试条件依赖"""
        # 添加任务
        self.dependency_manager.add_task("task_a")
        self.dependency_manager.add_task(
            "task_b",
            dependencies=[{
                "task_id": "task_a",
                "type": "conditional",
                "condition": lambda: True  # 总是满足条件
            }]
        )
        
        # 标记任务a完成
        self.dependency_manager.mark_task_completed("task_a")
        
        # 条件依赖应该满足
        self.assertTrue(self.dependency_manager.can_execute_task("task_b"))
    
    def test_resource_allocation(self):
        """测试资源分配"""
        # 添加需要资源的任务
        self.dependency_manager.add_task(
            "task_1",
            resource_requirements={"cpu": 50, "memory": 2048}
        )
        
        # 检查资源是否足够
        self.assertTrue(self.dependency_manager.can_execute_task("task_1"))
        
        # 添加另一个需要大量资源的任务
        self.dependency_manager.add_task(
            "task_2",
            resource_requirements={"cpu": 60, "memory": 4096}
        )
        
        # 两个任务同时执行时资源不足
        self.dependency_manager._executing_tasks.add("task_1")
        self.assertFalse(self.dependency_manager.can_execute_task("task_2"))
    
    def test_ready_tasks(self):
        """测试可执行任务列表"""
        # 添加任务
        self.dependency_manager.add_task("task_1")
        self.dependency_manager.add_task(
            "task_2",
            dependencies=[{"task_id": "task_1", "type": "required"}]
        )
        
        # 获取可执行任务
        ready_tasks = self.dependency_manager.get_ready_tasks()
        self.assertIn("task_1", ready_tasks)
        self.assertNotIn("task_2", ready_tasks)  # task_2依赖task_1
        
        # 标记task_1完成
        self.dependency_manager.mark_task_completed("task_1")
        
        # 现在task_2也可以执行
        ready_tasks = self.dependency_manager.get_ready_tasks()
        self.assertIn("task_2", ready_tasks)
    
    def test_task_status_tracking(self):
        """测试任务状态跟踪"""
        # 添加任务
        self.dependency_manager.add_task("test_task")
        
        # 获取任务状态
        status = self.dependency_manager.get_task_status("test_task")
        self.assertEqual(status["status"], "pending")
        
        # 标记任务完成
        self.dependency_manager.mark_task_completed("test_task", {"execution_time": 10.5})
        
        # 检查状态更新
        status = self.dependency_manager.get_task_status("test_task")
        self.assertEqual(status["status"], "completed")
        self.assertEqual(status["execution_time"], 10.5)
    
    def test_dependency_graph_info(self):
        """测试依赖图信息"""
        # 添加任务和依赖
        self.dependency_manager.add_task("task_1")
        self.dependency_manager.add_task("task_2")
        self.dependency_manager.add_task_dependency("task_2", "task_1")
        
        # 获取依赖图信息
        graph_info = self.dependency_manager.get_dependency_graph()
        
        # 验证信息完整性
        self.assertIn("tasks", graph_info)
        self.assertIn("execution_order", graph_info)
        self.assertIn("ready_tasks", graph_info)
        self.assertIn("executing_tasks", graph_info)
        self.assertIn("completed_tasks", graph_info)
        self.assertIn("failed_tasks", graph_info)


class TestResourceManager(unittest.TestCase):
    """资源管理器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.resource_manager = ResourceManager()
    
    def test_resource_allocation(self):
        """测试资源分配"""
        # 检查资源分配
        requirements = {"cpu": 20, "memory": 1024}
        self.assertTrue(self.resource_manager.can_allocate_resources(requirements))
        
        # 分配资源
        self.assertTrue(self.resource_manager.allocate_resources("task_1", requirements))
        
        # 检查剩余资源
        status = self.resource_manager.get_resource_status()
        self.assertEqual(status["cpu"]["allocated"], 20)
        self.assertEqual(status["memory"]["allocated"], 1024)
    
    def test_resource_insufficient(self):
        """测试资源不足"""
        # 分配大量资源
        large_requirements = {"cpu": 80, "memory": 6000}
        self.assertTrue(self.resource_manager.allocate_resources("task_1", large_requirements))
        
        # 尝试分配更多资源
        more_requirements = {"cpu": 30, "memory": 3000}
        self.assertFalse(self.resource_manager.can_allocate_resources(more_requirements))
    
    def test_resource_release(self):
        """测试资源释放"""
        # 分配资源
        requirements = {"cpu": 30, "memory": 2048}
        self.resource_manager.allocate_resources("task_1", requirements)
        
        # 释放资源
        self.resource_manager.release_resources(requirements)
        
        # 检查资源状态
        status = self.resource_manager.get_resource_status()
        self.assertEqual(status["cpu"]["allocated"], 0)
        self.assertEqual(status["memory"]["allocated"], 0)
    
    def test_resource_status(self):
        """测试资源状态"""
        # 分配一些资源
        self.resource_manager.allocate_resources("task_1", {"cpu": 25, "memory": 1024})
        
        # 获取状态
        status = self.resource_manager.get_resource_status()
        
        # 验证状态信息
        self.assertIn("cpu", status)
        self.assertIn("memory", status)
        self.assertEqual(status["cpu"]["total"], 100)
        self.assertEqual(status["cpu"]["allocated"], 25)
        self.assertEqual(status["cpu"]["available"], 75)
        self.assertEqual(status["cpu"]["utilization"], 25.0)


if __name__ == "__main__":
    unittest.main()
