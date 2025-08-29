#!/usr/bin/env python3
"""
自动化AI任务执行系统 - 主程序入口
"""

import sys
import logging
import signal
from pathlib import Path

from src.core import (
    ConfigManager, 
    StateManager, 
    StateFileManager, 
    TaskManager
)
from src.services import NotifyService


def setup_logging():
    """设置日志配置"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('logs/system.log', encoding='utf-8')
        ]
    )


def signal_handler(signum, frame):
    """信号处理器"""
    print(f"\n收到信号 {signum}，正在优雅关闭系统...")
    sys.exit(0)


def main():
    """主函数"""
    try:
        # 设置信号处理
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # 设置日志
        setup_logging()
        logger = logging.getLogger(__name__)
        
        logger.info("=" * 60)
        logger.info("自动化AI任务执行系统启动中...")
        logger.info("=" * 60)
        
        # 创建必要的目录
        Path("logs").mkdir(exist_ok=True)
        Path("states").mkdir(exist_ok=True)
        Path("archives").mkdir(exist_ok=True)
        Path("outputs").mkdir(exist_ok=True)
        Path("outputs/reviews").mkdir(exist_ok=True)
        Path("outputs/docs").mkdir(exist_ok=True)
        Path("outputs/requirement_reviews").mkdir(exist_ok=True)
        Path("outputs/custom_tasks").mkdir(exist_ok=True)
        
        # 初始化核心组件
        logger.info("初始化配置管理器...")
        config_manager = ConfigManager()
        
        logger.info("初始化状态管理器...")
        state_manager = StateManager()
        
        logger.info("初始化状态文件管理器...")
        state_file_manager = StateFileManager()
        
        logger.info("初始化通知服务...")
        notify_service = NotifyService(config_manager)
        
        logger.info("初始化任务管理器...")
        task_manager = TaskManager(
            config_manager=config_manager,
            state_manager=state_manager,
            notify_service=notify_service,
            max_workers=5
        )
        
        # 启动任务管理器
        logger.info("启动任务管理器...")
        task_manager.start()
        
        # 系统状态摘要
        logger.info("=" * 60)
        logger.info("系统初始化完成！")
        logger.info("=" * 60)
        
        # 显示系统信息
        system_config = config_manager.get_system_config()
        logger.info(f"系统名称: {system_config.get('name', '自动化AI任务执行系统')}")
        logger.info(f"系统版本: {system_config.get('version', '1.0.0')}")
        logger.info(f"最大并发任务数: {system_config.get('max_concurrent_tasks', 5)}")
        
        # 显示任务信息
        task_configs = config_manager.get_all_task_configs()
        logger.info(f"已配置任务数量: {len(task_configs)}")
        
        if task_configs:
            logger.info("任务列表:")
            for task_id, task_config in task_configs.items():
                task_type = task_config.get('type', 'unknown')
                enabled = task_config.get('enabled', True)
                status = "启用" if enabled else "禁用"
                logger.info(f"  - {task_id} ({task_type}) - {status}")
        
        # 显示调度器状态
        scheduler_stats = task_manager.get_scheduler_stats()
        logger.info(f"调度器状态: {'运行中' if scheduler_stats.get('running', False) else '已停止'}")
        logger.info(f"已调度任务数: {scheduler_stats.get('job_count', 0)}")
        
        logger.info("=" * 60)
        logger.info("系统已启动，按 Ctrl+C 停止系统")
        logger.info("=" * 60)
        
        # 保持系统运行
        try:
            while task_manager.is_running():
                # 每30秒检查一次系统状态
                import time
                time.sleep(30)
                
                # 显示运行状态
                running_tasks = task_manager.get_running_tasks()
                if running_tasks:
                    logger.info(f"当前运行中的任务: {', '.join(running_tasks)}")
                else:
                    logger.debug("当前没有运行中的任务")
                
        except KeyboardInterrupt:
            logger.info("收到键盘中断信号")
        
        # 优雅关闭
        logger.info("正在关闭系统...")
        task_manager.stop()
        state_file_manager.cleanup_expired_states()
        
        logger.info("系统已安全关闭")
        
    except Exception as e:
        logger.error(f"系统启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
