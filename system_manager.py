#!/usr/bin/env python3
"""
自动化AI任务执行系统 - 持久化系统管理脚本
解决CLI命令无法连接到运行中系统的问题
"""

import os
import sys
import time
import signal
import json
import logging
from pathlib import Path
from datetime import datetime
import subprocess
import threading

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from src.core import (
    ConfigManager, 
    StateManager, 
    StateFileManager, 
    TaskManager
)
from src.services import NotifyService

class PersistentSystemManager:
    """持久化系统管理器"""
    
    def __init__(self, config_dir="./config"):
        self.config_dir = config_dir
        self.pid_file = Path("system.pid")
        self.status_file = Path("system_status.json")
        self.running = False
        self.task_manager = None
        self.logger = self._setup_logging()
        
    def _setup_logging(self):
        """设置日志"""
        Path("logs").mkdir(exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/system_manager.log', encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        return logging.getLogger(__name__)
    
    def start_system(self):
        """启动系统"""
        if self.is_running():
            print("⚠️ 系统已在运行中")
            return False
            
        try:
            # 初始化组件
            config_manager = ConfigManager(self.config_dir)
            state_manager = StateManager()
            state_file_manager = StateFileManager(config_manager)
            notify_service = NotifyService(config_manager)
            
            self.task_manager = TaskManager(
                config_manager=config_manager,
                state_manager=state_manager,
                notify_service=notify_service
            )
            
            # 启动任务管理器
            self.task_manager.start()
            self.running = True
            
            # 保存PID和状态
            self._save_pid()
            self._save_status()
            
            # 启动状态监控线程
            self._start_monitor_thread()
            
            print("✅ 系统启动成功！")
            print("💡 使用 'python system_manager.py status' 查看状态")
            print("💡 使用 'python system_manager.py stop' 停止系统")
            print("💡 使用 'python system_manager.py run' 启动并持续运行")
            
            return True
            
        except Exception as e:
            self.logger.error(f"启动系统失败: {e}")
            print(f"❌ 启动系统失败: {e}")
            return False
    
    def stop_system(self):
        """停止系统"""
        if not self.is_running():
            print("⚠️ 系统未运行")
            return False
            
        try:
            if self.task_manager:
                self.task_manager.stop()
            
            self.running = False
            self._cleanup()
            
            print("✅ 系统已停止！")
            return True
            
        except Exception as e:
            self.logger.error(f"停止系统失败: {e}")
            print(f"❌ 停止系统失败: {e}")
            return False
    
    def get_status(self):
        """获取系统状态"""
        if not self.is_running():
            print("⚠️ 系统未运行")
            return None
            
        try:
            status = {
                'running': self.running,
                'task_manager_running': self.task_manager.is_running() if self.task_manager else False,
                'scheduler_stats': self.task_manager.get_scheduler_stats() if self.task_manager else {},
                'running_tasks': self.task_manager.get_running_tasks() if self.task_manager else [],
                'last_update': datetime.now().isoformat()
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"获取状态失败: {e}")
            return None
    
    def print_status(self):
        """打印系统状态"""
        status = self.get_status()
        if not status:
            return
            
        print("\n" + "="*60)
        print("🚀 自动化AI任务执行系统状态")
        print("="*60)
        
        print(f"🔄 系统运行状态: {'运行中' if status['running'] else '已停止'}")
        print(f"🔄 任务管理器状态: {'运行中' if status['task_manager_running'] else '已停止'}")
        
        scheduler_stats = status['scheduler_stats']
        print(f"⏰ 调度器状态: {'运行中' if scheduler_stats.get('running', False) else '已停止'}")
        print(f"📊 已调度任务数: {scheduler_stats.get('job_count', 0)}")
        
        running_tasks = status['running_tasks']
        if running_tasks:
            print(f"🏃 当前运行中的任务: {', '.join(running_tasks)}")
        else:
            print("💤 当前没有运行中的任务")
        
        print(f"🕒 最后更新: {status['last_update']}")
        print("="*60)
    
    def is_running(self):
        """检查系统是否运行"""
        if self.running:
            return True
            
        # 检查PID文件
        if self.pid_file.exists():
            try:
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                # 检查进程是否存在
                try:
                    os.kill(pid, 0)  # 发送信号0检查进程是否存在
                    return True
                except OSError:
                    # 进程不存在，清理PID文件
                    self.pid_file.unlink(missing_ok=True)
                    
            except (ValueError, FileNotFoundError):
                pass
                
        return False
    
    def _save_pid(self):
        """保存PID"""
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))
    
    def _save_status(self):
        """保存状态"""
        status = self.get_status()
        if status:
            with open(self.status_file, 'w') as f:
                json.dump(status, f, indent=2)
    
    def _cleanup(self):
        """清理文件"""
        self.pid_file.unlink(missing_ok=True)
        self.status_file.unlink(missing_ok=True)
    
    def _start_monitor_thread(self):
        """启动监控线程"""
        def monitor():
            while self.running:
                try:
                    self._save_status()
                    time.sleep(5)  # 每5秒更新一次状态
                except Exception as e:
                    self.logger.error(f"监控线程错误: {e}")
                    break
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    def run_forever(self):
        """运行系统直到收到停止信号"""
        def signal_handler(signum, frame):
            print("\n🛑 收到停止信号，正在关闭系统...")
            self.stop_system()
            sys.exit(0)
        
        # 注册信号处理器
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            print("🚀 系统运行中，按 Ctrl+C 停止...")
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            signal_handler(signal.SIGINT, None)

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python system_manager.py [start|stop|status|run]")
        sys.exit(1)
    
    command = sys.argv[1]
    manager = PersistentSystemManager()
    
    if command == "start":
        manager.start_system()
    elif command == "stop":
        manager.stop_system()
    elif command == "status":
        manager.print_status()
    elif command == "run":
        if manager.start_system():
            manager.run_forever()
    else:
        print(f"未知命令: {command}")
        print("可用命令: start, stop, status, run")

if __name__ == "__main__":
    main()
