"""
自动化AI任务执行系统 - CLI命令行接口
"""

import click
import sys
import logging
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core import (
    ConfigManager, 
    StateManager, 
    StateFileManager, 
    TaskManager
)
from src.services import NotifyService


def setup_logging(verbose: bool = False):
    """设置日志配置"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('logs/cli.log', encoding='utf-8')
        ]
    )


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='启用详细日志')
@click.option('--config', '-c', default='./config', help='配置文件目录路径')
@click.pass_context
def cli(ctx, verbose, config):
    """自动化AI任务执行系统 - 命令行管理工具"""
    ctx.ensure_object(dict)
    ctx.obj['config_dir'] = config
    ctx.obj['verbose'] = verbose
    
    # 设置日志
    setup_logging(verbose)
    
    # 创建必要的目录
    Path("logs").mkdir(exist_ok=True)
    Path("states").mkdir(exist_ok=True)
    Path("archives").mkdir(exist_ok=True)
    Path("outputs").mkdir(exist_ok=True)


@cli.command()
@click.pass_context
def status(ctx):
    """显示系统状态"""
    try:
        click.echo("🔍 检查系统状态...")
        
        # 初始化组件
        config_manager = ConfigManager(ctx.obj['config_dir'])
        state_manager = StateManager()
        state_file_manager = StateFileManager()
        notify_service = NotifyService(config_manager)
        task_manager = TaskManager(
            config_manager=config_manager,
            state_manager=state_manager,
            notify_service=notify_service
        )
        
        # 显示系统信息
        click.echo("\n" + "="*60)
        click.echo("🚀 自动化AI任务执行系统状态")
        click.echo("="*60)
        
        # 系统配置信息
        system_config = config_manager.get_system_config()
        click.echo(f"📋 系统名称: {system_config.get('name', '自动化AI任务执行系统')}")
        click.echo(f"🔢 系统版本: {system_config.get('version', '1.0.0')}")
        click.echo(f"⚙️ 最大并发任务数: {system_config.get('max_concurrent_tasks', 5)}")
        
        # 任务配置信息
        task_configs = config_manager.get_all_task_configs()
        click.echo(f"📝 已配置任务数量: {len(task_configs)}")
        
        if task_configs:
            click.echo("\n📋 任务列表:")
            for task_id, task_config in task_configs.items():
                task_type = task_config.get('type', 'unknown')
                enabled = task_config.get('enabled', True)
                status_icon = "✅" if enabled else "❌"
                click.echo(f"  {status_icon} {task_id} ({task_type})")
        
        # 任务管理器状态
        click.echo(f"\n🔄 任务管理器状态: {'运行中' if task_manager.is_running() else '已停止'}")
        
        # 调度器状态
        scheduler_stats = task_manager.get_scheduler_stats()
        click.echo(f"⏰ 调度器状态: {'运行中' if scheduler_stats.get('running', False) else '已停止'}")
        click.echo(f"📊 已调度任务数: {scheduler_stats.get('job_count', 0)}")
        
        # 运行中的任务
        running_tasks = task_manager.get_running_tasks()
        if running_tasks:
            click.echo(f"\n🏃 当前运行中的任务: {', '.join(running_tasks)}")
        else:
            click.echo("\n💤 当前没有运行中的任务")
        
        # 状态文件信息
        click.echo(f"\n📁 状态文件目录: {state_file_manager.work_dir}")
        state_files = list(state_file_manager.work_dir.glob("*.json"))
        click.echo(f"📄 状态文件数量: {len(state_files)}")
        
        click.echo("\n" + "="*60)
        
    except Exception as e:
        click.echo(f"❌ 获取系统状态失败: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('task_id')
@click.pass_context
def task_status(ctx, task_id):
    """显示指定任务的详细状态"""
    try:
        click.echo(f"🔍 检查任务状态: {task_id}")
        
        # 初始化组件
        config_manager = ConfigManager(ctx.obj['config_dir'])
        state_manager = StateManager()
        notify_service = NotifyService(config_manager)
        task_manager = TaskManager(
            config_manager=config_manager,
            state_manager=state_manager,
            notify_service=notify_service
        )
        
        # 获取任务状态
        task_status = task_manager.get_task_status(task_id)
        if not task_status:
            click.echo(f"❌ 任务不存在: {task_id}", err=True)
            sys.exit(1)
        
        # 显示任务状态
        click.echo("\n" + "="*50)
        click.echo(f"📋 任务状态详情: {task_id}")
        click.echo("="*50)
        
        click.echo(f"🆔 任务ID: {task_status.get('task_id')}")
        click.echo(f"🔄 运行状态: {'运行中' if task_status.get('is_running') else '未运行'}")
        click.echo(f"📊 任务状态: {task_status.get('status', 'unknown')}")
        click.echo(f"📈 进度: {task_status.get('progress', 0)}%")
        click.echo(f"🔄 尝试次数: {task_status.get('attempts', 0)}")
        click.echo(f"❌ 错误次数: {task_status.get('errors', 0)}")
        
        if task_status.get('last_run_time'):
            click.echo(f"⏰ 上次运行时间: {task_status.get('last_run_time')}")
        
        if task_status.get('next_run_time'):
            click.echo(f"⏰ 下次运行时间: {task_status.get('next_run_time')}")
        
        if task_status.get('executor'):
            click.echo(f"🔧 执行器: {task_status.get('executor')}")
        
        # 显示元数据
        metadata = task_status.get('metadata', {})
        if metadata:
            click.echo(f"\n📋 元数据:")
            for key, value in metadata.items():
                click.echo(f"  {key}: {value}")
        
        click.echo("\n" + "="*50)
        
    except Exception as e:
        click.echo(f"❌ 获取任务状态失败: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('task_id')
@click.pass_context
def run_task(ctx, task_id):
    """立即执行指定任务"""
    try:
        click.echo(f"🚀 立即执行任务: {task_id}")
        
        # 初始化组件
        config_manager = ConfigManager(ctx.obj['config_dir'])
        state_manager = StateManager()
        notify_service = NotifyService(config_manager)
        task_manager = TaskManager(
            config_manager=config_manager,
            state_manager=state_manager,
            notify_service=notify_service
        )
        
        # 检查任务是否存在
        task_config = config_manager.get_task_config(task_id)
        if not task_config:
            click.echo(f"❌ 任务配置不存在: {task_id}", err=True)
            sys.exit(1)
        
        # 检查任务是否已在运行
        if task_id in task_manager.get_running_tasks():
            click.echo(f"⚠️ 任务已在运行中: {task_id}", err=True)
            sys.exit(1)
        
        # 执行任务
        if task_manager.execute_task_now(task_id):
            click.echo(f"✅ 任务已提交执行: {task_id}")
            click.echo("💡 使用 'task-status' 命令查看执行状态")
        else:
            click.echo(f"❌ 任务执行失败: {task_id}", err=True)
            sys.exit(1)
        
    except Exception as e:
        click.echo(f"❌ 执行任务失败: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('task_id')
@click.pass_context
def execute_workflow(ctx, task_id):
    """使用工作流引擎执行指定任务"""
    try:
        click.echo(f"🚀 使用工作流引擎执行任务: {task_id}")
        
        # 初始化组件
        config_manager = ConfigManager(ctx.obj['config_dir'])
        state_manager = StateManager()
        notify_service = NotifyService(config_manager)
        task_manager = TaskManager(
            config_manager=config_manager,
            state_manager=state_manager,
            notify_service=notify_service
        )
        
        # 检查任务是否存在
        task_config = config_manager.get_task_config(task_id)
        if not task_config:
            click.echo(f"❌ 任务配置不存在: {task_id}", err=True)
            sys.exit(1)
        
        # 检查任务是否已在运行
        if task_id in task_manager.get_running_tasks():
            click.echo(f"⚠️ 任务已在运行中: {task_id}", err=True)
            sys.exit(1)
        
        # 执行工作流任务
        if task_manager.execute_task_with_workflow(task_id):
            click.echo(f"✅ 工作流任务已提交执行: {task_id}")
            click.echo("💡 使用 'task-status' 命令查看执行状态")
        else:
            click.echo(f"❌ 工作流任务执行失败: {task_id}", err=True)
            sys.exit(1)
        
    except Exception as e:
        click.echo(f"❌ 执行工作流任务失败: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('task_id')
@click.pass_context
def stop_task(ctx, task_id):
    """停止指定任务"""
    try:
        click.echo(f"🛑 停止任务: {task_id}")
        
        # 初始化组件
        config_manager = ConfigManager(ctx.obj['config_dir'])
        state_manager = StateManager()
        notify_service = NotifyService(config_manager)
        task_manager = TaskManager(
            config_manager=config_manager,
            state_manager=state_manager,
            notify_service=notify_service
        )
        
        # 停止任务
        if task_manager.stop_task(task_id):
            click.echo(f"✅ 任务已停止: {task_id}")
        else:
            click.echo(f"❌ 停止任务失败: {task_id}", err=True)
            sys.exit(1)
        
    except Exception as e:
        click.echo(f"❌ 停止任务失败: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def list_tasks(ctx):
    """列出所有任务"""
    try:
        click.echo("📋 列出所有任务...")
        
        # 初始化组件
        config_manager = ConfigManager(ctx.obj['config_dir'])
        state_manager = StateManager()
        notify_service = NotifyService(config_manager)
        task_manager = TaskManager(
            config_manager=config_manager,
            state_manager=state_manager,
            notify_service=notify_service
        )
        
        # 获取所有任务状态
        task_statuses = task_manager.get_all_task_statuses()
        
        if not task_statuses:
            click.echo("📭 没有找到任何任务")
            return
        
        # 显示任务列表
        click.echo("\n" + "="*80)
        click.echo(f"{'任务ID':<20} {'类型':<15} {'状态':<12} {'进度':<8} {'运行状态':<10}")
        click.echo("="*80)
        
        for task_status in task_statuses:
            task_id = task_status.get('task_id', 'N/A')
            task_type = task_status.get('metadata', {}).get('task_type', 'unknown')
            status = task_status.get('status', 'unknown')
            progress = f"{task_status.get('progress', 0)}%"
            is_running = "运行中" if task_status.get('is_running') else "未运行"
            
            click.echo(f"{task_id:<20} {task_type:<15} {status:<12} {progress:<8} {is_running:<10}")
        
        click.echo("="*80)
        
    except Exception as e:
        click.echo(f"❌ 列出任务失败: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def start_system(ctx):
    """启动系统"""
    try:
        click.echo("🚀 启动自动化AI任务执行系统...")
        
        # 初始化组件
        config_manager = ConfigManager(ctx.obj['config_dir'])
        state_manager = StateManager()
        state_file_manager = StateFileManager()
        notify_service = NotifyService(config_manager)
        task_manager = TaskManager(
            config_manager=config_manager,
            state_manager=state_manager,
            notify_service=notify_service
        )
        
        # 启动任务管理器
        task_manager.start()
        
        click.echo("✅ 系统启动成功！")
        click.echo("💡 使用 'status' 命令查看系统状态")
        click.echo("💡 使用 'list-tasks' 命令查看任务列表")
        
    except Exception as e:
        click.echo(f"❌ 启动系统失败: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def stop_system(ctx):
    """停止系统"""
    try:
        click.echo("🛑 停止自动化AI任务执行系统...")
        
        # 初始化组件
        config_manager = ConfigManager(ctx.obj['config_dir'])
        state_manager = StateManager()
        state_file_manager = StateFileManager()
        notify_service = NotifyService(config_manager)
        task_manager = TaskManager(
            config_manager=config_manager,
            state_manager=state_manager,
            notify_service=notify_service
        )
        
        # 停止任务管理器
        task_manager.stop()
        
        # 清理状态文件
        cleaned_count = state_file_manager.cleanup_expired_states()
        
        click.echo("✅ 系统已停止！")
        if cleaned_count > 0:
            click.echo(f"🧹 清理了 {cleaned_count} 个过期状态文件")
        
    except Exception as e:
        click.echo(f"❌ 停止系统失败: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def cleanup(ctx):
    """清理系统"""
    try:
        click.echo("🧹 清理系统...")
        
        # 初始化组件
        state_file_manager = StateFileManager()
        
        # 清理过期状态文件
        cleaned_count = state_file_manager.cleanup_expired_states()
        click.echo(f"✅ 清理了 {cleaned_count} 个过期状态文件")
        
        # 获取归档信息
        archive_info = state_file_manager.get_archive_info()
        if archive_info:
            click.echo(f"📦 归档文件总数: {archive_info.get('total_archives', 0)}")
            click.echo(f"💾 归档总大小: {archive_info.get('total_size_mb', 0):.2f} MB")
        
    except Exception as e:
        click.echo(f"❌ 清理系统失败: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def version(ctx):
    """显示版本信息"""
    click.echo("🚀 自动化AI任务执行系统 v1.0.0")
    click.echo("📅 2024年")
    click.echo("👥 Auto Coder Team")


if __name__ == '__main__':
    cli()
