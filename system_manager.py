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
import atexit

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
        self.log_file = Path("logs/system_manager.log")
        self.running = False
        self.task_manager = None
        self.logger = None
        self.is_daemon = False
        
    def _setup_logging(self, daemon_mode=False):
        """设置日志"""
        Path("logs").mkdir(exist_ok=True)
        
        # 在daemon模式下，只写入文件，不输出到控制台
        handlers = [logging.FileHandler(self.log_file, encoding='utf-8')]
        if not daemon_mode:
            handlers.append(logging.StreamHandler(sys.stdout))
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(levelname)s - %(asctime)s - %(name)s - %(message)s',
            handlers=handlers
        )
        
        # 添加颜色支持
        class ColoredFormatter(logging.Formatter):
            """带颜色的日志格式化器"""
            COLORS = {
                'ERROR': '\033[91m',    # 红色
                'WARNING': '\033[93m',  # 黄色
                'INFO': '\033[94m',     # 蓝色
                'DEBUG': '\033[90m',    # 灰色
                'RESET': '\033[0m'      # 重置
            }
            
            def format(self, record):
                # 添加颜色标记
                if record.levelname in self.COLORS:
                    record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
                return super().format(record)
        
        # 应用颜色格式化器到控制台处理器
        if not daemon_mode:
            for handler in logging.getLogger().handlers:
                if isinstance(handler, logging.StreamHandler):
                    handler.setFormatter(ColoredFormatter('%(levelname)s - %(asctime)s - %(name)s - %(message)s'))
        self.logger = logging.getLogger(__name__)
    
    def _check_existing_process(self):
        """检查是否已有进程在运行"""
        if self.pid_file.exists():
            try:
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                # 检查进程是否存在
                try:
                    import platform
                    if platform.system() == 'Windows':
                        # Windows系统下使用tasklist检查进程
                        import subprocess
                        result = subprocess.run(['tasklist', '/FI', f'PID eq {pid}'], 
                                              capture_output=True, text=True, shell=True)
                        # 检查输出中是否包含进程信息（不仅仅是PID数字）
                        if 'python.exe' in result.stdout or 'python' in result.stdout:
                            return pid
                        else:
                            # 进程不存在，清理PID文件
                            self.pid_file.unlink(missing_ok=True)
                    else:
                        # Unix系统下使用kill信号检查
                        os.kill(pid, 0)  # 发送信号0检查进程是否存在
                        return pid
                except (OSError, subprocess.SubprocessError):
                    # 进程不存在，清理PID文件
                    self.pid_file.unlink(missing_ok=True)
                    
            except (ValueError, FileNotFoundError):
                pass
                
        return None
    
    def start_system(self, daemon_mode=False):
        """启动系统"""
        self.is_daemon = daemon_mode
        
        # 检查是否已有进程在运行
        existing_pid = self._check_existing_process()
        if existing_pid:
            print(f"⚠️  系统已在运行中 (PID: {existing_pid})")
            print("💡 使用 'python system_manager.py status' 查看状态")
            print("💡 使用 'python system_manager.py stop' 停止系统")
            return False
            
        try:
            # 设置日志
            self._setup_logging(daemon_mode)
            
            # 初始化组件
            self.logger.debug("初始化配置管理器...")
            config_manager = ConfigManager(self.config_dir)
            
            self.logger.debug("初始化状态管理器...")
            state_manager = StateManager()
            
            self.logger.debug("初始化状态文件管理器...")
            state_file_manager = StateFileManager(config_manager)
            
            self.logger.debug("初始化通知服务...")
            notify_service = NotifyService(config_manager)
            
            self.logger.debug("初始化任务管理器...")
            self.task_manager = TaskManager(
                config_manager=config_manager,
                state_manager=state_manager,
                notify_service=notify_service
            )
            
            # 启动任务管理器
            self.logger.debug("启动任务管理器...")
            self.task_manager.start()
            self.running = True
            
            # 保存PID和状态
            self._save_pid()
            self._save_status()
            
            # 启动状态监控线程
            self._start_monitor_thread()
            
            # 注册清理函数
            atexit.register(self._cleanup_on_exit)
            
            if not daemon_mode:
                print("✅ 系统启动成功！")
                print("💡 使用 'python system_manager.py status' 查看状态")
                print("💡 使用 'python system_manager.py stop' 停止系统")
                print("💡 使用 'python system_manager.py run' 启动并持续运行")
            else:
                self.logger.info("✅ 系统启动成功！")
                print("✅ 系统已在后台启动成功！")
                print(f"📝 日志文件: {self.log_file}")
                print(f"🆔 进程ID: {os.getpid()}")
                print("💡 使用 'python system_manager.py status' 查看状态")
                print("💡 使用 'python system_manager.py stop' 停止系统")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"启动系统失败: {e}")
            print(f"❌ 启动系统失败: {e}")
            return False
    
    def stop_system(self):
        """停止系统"""
        # 检查是否已有进程在运行
        existing_pid = self._check_existing_process()
        if not existing_pid:
            print("⚠️ 系统未运行")
            return False
            
        try:
            # 尝试优雅地停止进程
            print(f"🛑 正在停止系统 (PID: {existing_pid})...")
            os.kill(existing_pid, signal.SIGTERM)
            
            # 等待进程结束
            for i in range(10):  # 最多等待10秒
                try:
                    os.kill(existing_pid, 0)
                    time.sleep(1)
                except OSError:
                    break
            
            # 如果进程还在运行，强制终止
            try:
                os.kill(existing_pid, 0)
                print("⚠️ 强制终止进程...")
                os.kill(existing_pid, signal.SIGKILL)
            except OSError:
                pass
            
            # 清理文件
            self._cleanup()
            
            print("✅ 系统已停止！")
            return True
            
        except Exception as e:
            print(f"❌ 停止系统失败: {e}")
            return False
    
    def get_status(self):
        """获取系统状态"""
        try:
            # 首先尝试从状态文件读取信息
            if self.status_file.exists():
                with open(self.status_file, 'r') as f:
                    status = json.load(f)
                
                # 检查进程是否还在运行
                existing_pid = self._check_existing_process()
                if existing_pid:
                    status['pid'] = existing_pid
                    return status
                elif status.get('running', False):
                    # 状态文件显示系统在运行，但进程不存在，可能是异常退出
                    print("⚠️ 系统状态异常：状态文件显示系统在运行，但进程不存在")
                    print("🔄 正在清理异常状态文件...")
                    self._cleanup()
                    print("⚠️ 系统未运行")
                    return None
                else:
                    return None
            else:
                # 如果状态文件不存在，检查PID文件
                existing_pid = self._check_existing_process()
                if existing_pid:
                    # 有PID文件但没有状态文件，返回基本信息
                    return {
                        'running': True,
                        'pid': existing_pid,
                        'task_manager_running': 'unknown',
                        'scheduler_stats': {'running': 'unknown', 'job_count': 'unknown'},
                        'running_tasks': [],
                        'last_update': 'unknown'
                    }
                else:
                    print("⚠️ 系统未运行")
                    return None
            
        except Exception as e:
            print(f"❌ 获取状态失败: {e}")
            return None
    
    def print_status(self):
        """打印系统状态"""
        status = self.get_status()
        if not status:
            return
            
        print("\n" + "="*60)
        print("🚀 自动化AI任务执行系统状态")
        print("="*60)
        
        print(f"🔄 系统运行状态: {'运行中' if status.get('running', True) else '已停止'}")
        print(f"🆔 进程ID: {status.get('pid', 'unknown')}")
        
        task_manager_running = status.get('task_manager_running', 'unknown')
        if task_manager_running != 'unknown':
            print(f"🔄 任务管理器状态: {'运行中' if task_manager_running else '已停止'}")
        
        scheduler_stats = status.get('scheduler_stats', {})
        scheduler_running = scheduler_stats.get('running', 'unknown')
        if scheduler_running != 'unknown':
            print(f"⏰ 调度器状态: {'运行中' if scheduler_running else '已停止'}")
        
        job_count = scheduler_stats.get('job_count', 'unknown')
        if job_count != 'unknown':
            print(f"📊 已调度任务数: {job_count}")
        
        running_tasks = status.get('running_tasks', [])
        if running_tasks:
            print(f"🏃 当前运行中的任务: {', '.join(running_tasks)}")
        else:
            print("💤 当前没有运行中的任务")
        
        last_update = status.get('last_update', 'unknown')
        if last_update != 'unknown':
            print(f"🕒 最后更新: {last_update}")
        
        print("="*60)
    
    def is_running(self):
        """检查系统是否运行"""
        return self._check_existing_process() is not None
    
    def _save_pid(self):
        """保存PID"""
        try:
            with open(self.pid_file, 'w') as f:
                f.write(str(os.getpid()))
            if self.logger:
                self.logger.info(f"PID文件已保存: {self.pid_file} -> {os.getpid()}")
        except Exception as e:
            if self.logger:
                self.logger.error(f"保存PID文件失败: {e}")
    
    def _save_status(self):
        """保存状态"""
        try:
            status = {
                'running': self.running,
                'task_manager_running': self.task_manager.is_running() if self.task_manager else False,
                'scheduler_stats': self.task_manager.get_scheduler_stats() if self.task_manager else {},
                'running_tasks': self.task_manager.get_running_tasks() if self.task_manager else [],
                'last_update': datetime.now().isoformat()
            }
            
            with open(self.status_file, 'w') as f:
                json.dump(status, f, indent=2)
        except Exception as e:
            if self.logger:
                self.logger.error(f"保存状态失败: {e}")
    
    def _cleanup(self):
        """清理文件"""
        self.pid_file.unlink(missing_ok=True)
        self.status_file.unlink(missing_ok=True)
    
    def _cleanup_on_exit(self):
        """退出时清理"""
        # 只有在明确停止时才清理文件
        if not self.running:
            self._cleanup()
    
    def _start_monitor_thread(self):
        """启动监控线程"""
        def monitor():
            while self.running:
                try:
                    self._save_status()
                    time.sleep(5)  # 每5秒更新一次状态
                except Exception as e:
                    if self.logger:
                        self.logger.error(f"监控线程错误: {e}")
                    break
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    def run_forever(self):
        """运行系统直到收到停止信号"""
        def signal_handler(signum, frame):
            if not self.is_daemon:
                print("\n🛑 收到停止信号，正在关闭系统...")
            if self.logger:
                self.logger.info("收到停止信号，正在关闭系统...")
            self.stop_system()
            sys.exit(0)
        
        # 注册信号处理器
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            if not self.is_daemon:
                print("🚀 系统运行中，按 Ctrl+C 停止...")
            if self.logger:
                self.logger.info("系统运行中...")
            
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            signal_handler(signal.SIGINT, None)

def daemonize():
    """将进程转换为daemon进程"""
    import platform
    
    if platform.system() == 'Windows':
        # Windows系统下使用subprocess启动后台进程
        print("⚠️  Windows系统不支持daemon模式，将使用后台进程模式")
        return
    
    try:
        # 第一次fork
        pid = os.fork()
        if pid > 0:
            # 父进程退出
            sys.exit(0)
    except OSError as err:
        sys.stderr.write(f'fork #1 failed: {err}\n')
        sys.exit(1)
    
    # 分离父目录
    os.chdir('/')
    # 创建新会话
    os.umask(0)
    os.setsid()
    
    try:
        # 第二次fork
        pid = os.fork()
        if pid > 0:
            # 父进程退出
            sys.exit(0)
    except OSError as err:
        sys.stderr.write(f'fork #2 failed: {err}\n')
        sys.exit(1)
    
    # 重定向标准文件描述符
    sys.stdout.flush()
    sys.stderr.flush()
    with open('/dev/null', 'r') as f:
        os.dup2(f.fileno(), sys.stdin.fileno())
    with open('/dev/null', 'a+') as f:
        os.dup2(f.fileno(), sys.stdout.fileno())
    with open('/dev/null', 'a+') as f:
        os.dup2(f.fileno(), sys.stderr.fileno())

def start_background_process():
    """在Windows系统下启动后台进程"""
    import platform
    
    if platform.system() != 'Windows':
        return False
    
    try:
        # 直接在当前进程中启动系统，但设置为daemon模式
        manager = PersistentSystemManager()
        if manager.start_system(daemon_mode=True):
            # 启动一个后台线程来运行系统
            def run_system():
                manager.run_forever()
            
            import threading
            thread = threading.Thread(target=run_system, daemon=True)
            thread.start()
            
            print(f"✅ 后台进程启动成功 (PID: {os.getpid()})")
            return True
        else:
            print("❌ 后台进程启动失败")
            return False
            
    except Exception as e:
        print(f"❌ 启动后台进程失败: {e}")
        return False

def main():
    """主函数"""
    if len(sys.argv) < 2 or sys.argv[1] in ['--help', '-h', 'help']:
        print("用法: python system_manager.py [start|stop|status|run|daemon]")
        print("命令说明:")
        print("  start   - 启动系统（前台运行）")
        print("  stop    - 停止系统")
        print("  status  - 查看系统状态")
        print("  run     - 启动系统并持续运行（前台）")
        print("  daemon  - 启动系统（后台运行）")
        print("")
        print("示例:")
        print("  python system_manager.py daemon  # 后台启动系统")
        print("  python system_manager.py status  # 查看系统状态")
        print("  python system_manager.py stop    # 停止系统")
        sys.exit(1)
    
    command = sys.argv[1]
    manager = PersistentSystemManager()
    
    if command == "start":
        manager.start_system(daemon_mode=False)
    elif command == "stop":
        manager.stop_system()
    elif command == "status":
        manager.print_status()
    elif command == "run":
        if manager.start_system(daemon_mode=False):
            manager.run_forever()
    elif command == "daemon":
        # 检查是否已有进程在运行
        if manager.is_running():
            existing_pid = manager._check_existing_process()
            print(f"⚠️  系统已在运行中 (PID: {existing_pid})")
            print("💡 使用 'python system_manager.py status' 查看状态")
            print("💡 使用 'python system_manager.py stop' 停止系统")
            sys.exit(1)
        
        import platform
        if platform.system() == 'Windows':
            # Windows系统下直接启动系统并保持运行
            print("🚀 正在启动后台服务...")
            if manager.start_system(daemon_mode=True):
                print("✅ 系统已在后台启动成功！")
                print(f"📝 日志文件: {manager.log_file}")
                print(f"🆔 进程ID: {os.getpid()}")
                print("💡 使用 'python system_manager.py status' 查看状态")
                print("💡 使用 'python system_manager.py stop' 停止系统")
                print("🚀 系统运行中，按 Ctrl+C 停止...")
                
                # 保持主线程运行
                try:
                    while manager.running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n🛑 收到停止信号，正在关闭系统...")
                    manager.stop_system()
            else:
                sys.exit(1)
        else:
            # Unix系统下使用daemon模式
            print("🚀 正在启动后台服务...")
            # 转换为daemon进程
            daemonize()
            
            # 在daemon进程中启动系统
            if manager.start_system(daemon_mode=True):
                manager.run_forever()
            else:
                sys.exit(1)
    else:
        print(f"未知命令: {command}")
        print("可用命令: start, stop, status, run, daemon")

if __name__ == "__main__":
    main()
