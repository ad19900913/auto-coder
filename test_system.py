#!/usr/bin/env python3
"""
自动化AI任务执行系统 - 基本功能测试脚本
用于验证系统的核心功能是否正常工作
"""

import sys
import os
import logging
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

def setup_logging():
    """设置测试日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('./logs/test.log', encoding='utf-8')
        ]
    )

def test_imports():
    """测试模块导入"""
    print("🔍 测试模块导入...")
    
    try:
        from src.core import (
            ConfigManager, 
            StateManager, 
            StateFileManager, 
            TaskManager,
            WorkflowEngine
        )
        print("✅ 核心模块导入成功")
        
        from src.services import (
            NotifyService,
            AIService,
            GitService
        )
        print("✅ 服务模块导入成功")
        
        from src.tasks import (
            CodingTaskExecutor,
            ReviewTaskExecutor,
            DocTaskExecutor,
            RequirementReviewTaskExecutor,
            CustomTaskExecutor
        )
        print("✅ 任务执行器模块导入成功")
        
        return True
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_config_manager():
    """测试配置管理器"""
    print("\n🔍 测试配置管理器...")
    
    try:
        from src.core import ConfigManager
        
        # 创建配置管理器
        config_manager = ConfigManager("./config")
        
        # 测试获取系统配置
        system_config = config_manager.get_system_config()
        print(f"✅ 系统配置加载成功: {len(system_config)} 个配置项")
        
        # 测试获取任务配置
        task_configs = config_manager.get_all_task_configs()
        print(f"✅ 任务配置加载成功: {len(task_configs)} 个任务")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置管理器测试失败: {e}")
        return False

def test_workflow_engine():
    """测试工作流引擎"""
    print("\n🔍 测试工作流引擎...")
    
    try:
        from src.core import ConfigManager, WorkflowEngine
        
        # 创建配置管理器
        config_manager = ConfigManager("./config")
        
        # 创建工作流引擎
        workflow_engine = WorkflowEngine(config_manager)
        
        # 测试列出工作流模板
        templates = workflow_engine.list_workflow_templates()
        print(f"✅ 工作流模板加载成功: {len(templates)} 个模板")
        
        # 测试加载特定工作流模板
        try:
            template = workflow_engine.load_workflow_template("coding")
            print("✅ 编码工作流模板加载成功")
        except FileNotFoundError:
            print("⚠️ 编码工作流模板文件不存在，这是正常的")
        
        return True
        
    except Exception as e:
        print(f"❌ 工作流引擎测试失败: {e}")
        return False

def test_task_manager():
    """测试任务管理器"""
    print("\n🔍 测试任务管理器...")
    
    try:
        from src.core import ConfigManager, StateManager, TaskManager
        from src.services import NotifyService
        
        # 创建组件
        config_manager = ConfigManager("./config")
        state_manager = StateManager()
        notify_service = NotifyService(config_manager)
        
        # 创建任务管理器
        task_manager = TaskManager(
            config_manager=config_manager,
            state_manager=state_manager,
            notify_service=notify_service
        )
        
        print("✅ 任务管理器创建成功")
        
        # 测试获取任务状态
        task_statuses = task_manager.get_all_task_statuses()
        print(f"✅ 任务状态获取成功: {len(task_statuses)} 个任务状态")
        
        return True
        
    except Exception as e:
        print(f"❌ 任务管理器测试失败: {e}")
        return False

def test_cli_commands():
    """测试CLI命令"""
    print("\n🔍 测试CLI命令...")
    
    try:
        from src.cli.main import cli
        print("✅ CLI模块导入成功")
        
        # 这里可以添加更多CLI测试
        # 由于CLI需要实际运行，这里只测试导入
        
        return True
        
    except Exception as e:
        print(f"❌ CLI命令测试失败: {e}")
        return False

def test_directory_structure():
    """测试目录结构"""
    print("\n🔍 测试目录结构...")
    
    required_dirs = [
        "src",
        "src/core",
        "src/services", 
        "src/tasks",
        "src/cli",
        "config",
        "config/tasks",
        "workflows",
        "workflows/base",
        "workflows/coding",
        "workflows/review",
        "workflows/doc",
        "workflows/requirement_review",
        "workflows/custom",
        "prompts",
        "prompts/coding",
        "prompts/review",
        "prompts/doc",
        "prompts/requirement_review",
        "prompts/custom",
        "docs"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"❌ 缺少目录: {missing_dirs}")
        return False
    else:
        print("✅ 目录结构完整")
        return True

def test_config_files():
    """测试配置文件"""
    print("\n🔍 测试配置文件...")
    
    required_files = [
        "config/global_config.yaml",
        "config/tasks/coding_task_example.yaml",
        "config/tasks/review_task_example.yaml",
        "config/tasks/doc_task_example.yaml",
        "workflows/base/base_workflow.yaml",
        "workflows/coding/coding_workflow.yaml",
        "workflows/review/review_workflow.yaml",
        "workflows/doc/doc_workflow.yaml",
        "workflows/requirement_review/req_review_workflow.yaml",
        "workflows/custom/custom_workflow.yaml",
        "prompts/coding/coding_init_prompt.md",
        "prompts/review/review_init_prompt.md",
        "prompts/doc/doc_init_prompt.md",
        "prompts/requirement_review/req_review_init_prompt.md",
        "prompts/custom/custom_init_prompt.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ 缺少文件: {missing_files}")
        return False
    else:
        print("✅ 配置文件完整")
        return True

def main():
    """主测试函数"""
    print("🚀 自动化AI任务执行系统 - 基本功能测试")
    print("=" * 60)
    
    # 设置日志
    setup_logging()
    
    # 测试结果
    test_results = []
    
    # 执行测试
    test_results.append(("模块导入", test_imports()))
    test_results.append(("目录结构", test_directory_structure()))
    test_results.append(("配置文件", test_config_files()))
    test_results.append(("配置管理器", test_config_manager()))
    test_results.append(("工作流引擎", test_workflow_engine()))
    test_results.append(("任务管理器", test_task_manager()))
    test_results.append(("CLI命令", test_cli_commands()))
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print("=" * 60)
    print(f"总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统基本功能正常")
        return 0
    else:
        print("⚠️ 部分测试失败，请检查相关配置")
        return 1

if __name__ == "__main__":
    sys.exit(main())
