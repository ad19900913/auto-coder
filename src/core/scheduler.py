"""
任务调度器 - 基于APScheduler的任务调度管理
"""

import logging
import time
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR


class TaskScheduler:
    """任务调度器，管理定时任务的调度和执行"""
    
    def __init__(self, config_manager, max_workers: int = 5):
        """
        初始化任务调度器
        
        Args:
            config_manager: 配置管理器实例
            max_workers: 最大工作线程数
        """
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        self.max_workers = max_workers
        
        # 初始化调度器
        self._init_scheduler()
        
        # 任务执行器映射
        self.task_executors = {}
        
        # 任务状态跟踪
        self.task_status = {}
    
    def _init_scheduler(self):
        """初始化APScheduler调度器"""
        try:
            # 配置作业存储和执行器
            jobstores = {
                'default': MemoryJobStore()
            }
            
            executors = {
                'default': ThreadPoolExecutor(max_workers=self.max_workers)
            }
            
            job_defaults = {
                'coalesce': False,
                'max_instances': 1,
                'misfire_grace_time': 60
            }
            
            # 创建调度器
            self.scheduler = BackgroundScheduler(
                jobstores=jobstores,
                executors=executors,
                job_defaults=job_defaults,
                timezone='UTC'
            )
            
            # 添加事件监听器
            self.scheduler.add_listener(self._job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
            
            self.logger.debug("任务调度器初始化成功")
            
        except Exception as e:
            self.logger.error(f"任务调度器初始化失败: {e}")
            raise
    
    def start(self):
        """启动调度器"""
        try:
            if not self.scheduler.running:
                self.scheduler.start()
                self.logger.info("任务调度器启动成功")
            else:
                self.logger.info("任务调度器已在运行")
        except Exception as e:
            self.logger.error(f"启动任务调度器失败: {e}")
            raise
    
    def stop(self):
        """停止调度器"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown(wait=True)
                self.logger.info("任务调度器已停止")
            else:
                self.logger.info("任务调度器未在运行")
        except Exception as e:
            self.logger.error(f"停止任务调度器失败: {e}")
    
    def add_task(self, task_id: str, task_func: Callable, schedule_config: Dict[str, Any],
                 priority: int = 1, **kwargs) -> bool:
        """
        添加定时任务
        
        Args:
            task_id: 任务ID
            task_func: 任务执行函数
            schedule_config: 调度配置
            priority: 任务优先级（1-10，数字越大优先级越高）
            **kwargs: 其他任务参数
            
        Returns:
            是否添加成功
        """
        try:
            # 解析调度配置
            triggers = self._parse_schedule_config(schedule_config)
            if not triggers:
                self.logger.error(f"无效的调度配置: {schedule_config}")
                return False
            
            # 支持多个调度配置，为每个触发器创建一个任务
            jobs = []
            for i, trigger in enumerate(triggers):
                job_id = f"{task_id}_{i}" if len(triggers) > 1 else task_id
                job_name = f"Task_{task_id}_{i}" if len(triggers) > 1 else f"Task_{task_id}"
                
                job = self.scheduler.add_job(
                    func=task_func,
                    trigger=trigger,
                    id=job_id,
                    name=job_name,
                    args=[task_id],
                    kwargs=kwargs,
                    replace_existing=True,
                    misfire_grace_time=60
                )
                jobs.append(job)
            
            # 记录任务信息（如果有多个触发器，记录第一个）
            job = jobs[0]
            
            # 记录任务信息
            self.task_status[task_id] = {
                'job_id': job.id,
                'next_run_time': job.next_run_time,
                'priority': priority,
                'status': 'scheduled',
                'created_at': datetime.now().isoformat()
            }
            
            self.logger.info(f"任务添加成功: {task_id}, 下次执行时间: {job.next_run_time}")
            return True
            
        except Exception as e:
            self.logger.error(f"添加任务失败 {task_id}: {e}")
            return False
    
    def remove_task(self, task_id: str) -> bool:
        """
        移除定时任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否移除成功
        """
        try:
            if self.scheduler.get_job(task_id):
                self.scheduler.remove_job(task_id)
                
                # 更新任务状态
                if task_id in self.task_status:
                    self.task_status[task_id]['status'] = 'removed'
                
                self.logger.info(f"任务移除成功: {task_id}")
                return True
            else:
                self.logger.warning(f"任务不存在: {task_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"移除任务失败 {task_id}: {e}")
            return False
    
    def pause_task(self, task_id: str) -> bool:
        """
        暂停定时任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否暂停成功
        """
        try:
            job = self.scheduler.get_job(task_id)
            if job:
                job.pause()
                
                # 更新任务状态
                if task_id in self.task_status:
                    self.task_status[task_id]['status'] = 'paused'
                
                self.logger.info(f"任务暂停成功: {task_id}")
                return True
            else:
                self.logger.warning(f"任务不存在: {task_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"暂停任务失败 {task_id}: {e}")
            return False
    
    def resume_task(self, task_id: str) -> bool:
        """
        恢复定时任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否恢复成功
        """
        try:
            job = self.scheduler.get_job(task_id)
            if job:
                job.resume()
                
                # 更新任务状态
                if task_id in self.task_status:
                    self.task_status[task_id]['status'] = 'scheduled'
                
                self.logger.info(f"任务恢复成功: {task_id}")
                return True
            else:
                self.logger.warning(f"任务不存在: {task_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"恢复任务失败 {task_id}: {e}")
            return False
    
    def trigger_task(self, task_id: str) -> bool:
        """
        立即触发任务执行
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否触发成功
        """
        try:
            job = self.scheduler.get_job(task_id)
            if job:
                job.modify(next_run_time=datetime.now())
                self.logger.info(f"任务触发成功: {task_id}")
                return True
            else:
                self.logger.warning(f"任务不存在: {task_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"触发任务失败 {task_id}: {e}")
            return False
    
    def get_task_info(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取任务信息
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务信息字典
        """
        try:
            job = self.scheduler.get_job(task_id)
            if not job:
                return None
            
            task_info = {
                'id': job.id,
                'name': job.name,
                'func': job.func.__name__,
                'trigger': str(job.trigger),
                'next_run_time': job.next_run_time,
                'args': job.args,
                'kwargs': job.kwargs
            }
            
            # 合并状态信息
            if task_id in self.task_status:
                task_info.update(self.task_status[task_id])
            
            return task_info
            
        except Exception as e:
            self.logger.error(f"获取任务信息失败 {task_id}: {e}")
            return None
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """
        获取所有任务信息
        
        Returns:
            任务信息列表
        """
        try:
            tasks = []
            for job in self.scheduler.get_jobs():
                task_info = self.get_task_info(job.id)
                if task_info:
                    tasks.append(task_info)
            
            # 按优先级排序
            tasks.sort(key=lambda x: x.get('priority', 1), reverse=True)
            
            return tasks
            
        except Exception as e:
            self.logger.error(f"获取所有任务信息失败: {e}")
            return []
    
    def get_running_tasks(self) -> List[str]:
        """
        获取正在运行的任务ID列表
        
        Returns:
            正在运行的任务ID列表
        """
        try:
            running_tasks = []
            for task_id, status in self.task_status.items():
                if status.get('status') == 'running':
                    running_tasks.append(task_id)
            
            return running_tasks
            
        except Exception as e:
            self.logger.error(f"获取运行中任务失败: {e}")
            return []
    
    def _parse_schedule_config(self, config: Dict[str, Any]):
        """
        解析调度配置
        
        Args:
            config: 调度配置字典
            
        Returns:
            APScheduler触发器对象列表（支持多个调度配置）
        """
        try:
            schedule_type = config.get('type', 'cron')
            triggers = []
            
            if schedule_type == 'cron':
                # 支持两种cron配置格式：
                # 1. 标准crontab表达式格式 (设计文档格式)
                # 2. 分解的cron字段格式 (现有代码格式)
                
                # 检查是否有标准crontab表达式
                cron_expressions = config.get('cron_expressions', [])
                if cron_expressions:
                    # 使用设计文档格式：标准crontab表达式
                    for cron_expr in cron_expressions:
                        try:
                            # 解析标准crontab表达式 "0 9 * * *"
                            parts = cron_expr.split()
                            if len(parts) == 5:
                                minute, hour, day, month, day_of_week = parts
                                trigger = CronTrigger(
                                    minute=minute,
                                    hour=hour,
                                    day=day,
                                    month=month,
                                    day_of_week=day_of_week
                                )
                                triggers.append(trigger)
                            else:
                                self.logger.warning(f"无效的cron表达式: {cron_expr}")
                        except Exception as e:
                            self.logger.warning(f"解析cron表达式失败 {cron_expr}: {e}")
                
                # 检查是否有分解的cron字段配置（向后兼容）
                cron_config = config.get('cron', {})
                if cron_config and not triggers:
                    # 使用现有代码格式：分解的cron字段
                    trigger = CronTrigger(
                        year=cron_config.get('year', '*'),
                        month=cron_config.get('month', '*'),
                        week=cron_config.get('week', '*'),
                        day_of_week=cron_config.get('day_of_week', '*'),
                        day=cron_config.get('day', '*'),
                        hour=cron_config.get('hour', '*'),
                        minute=cron_config.get('minute', '*'),
                        second=cron_config.get('second', '0')
                    )
                    triggers.append(trigger)
                
                # 如果没有找到任何cron配置，记录警告
                if not triggers:
                    self.logger.warning("未找到有效的cron配置")
                    return None
            
            elif schedule_type == 'interval':
                # 间隔调度
                interval_config = config.get('interval', {})
                trigger = IntervalTrigger(
                    seconds=interval_config.get('seconds', 0),
                    minutes=interval_config.get('minutes', 0),
                    hours=interval_config.get('hours', 0),
                    days=interval_config.get('days', 0),
                    weeks=interval_config.get('weeks', 0)
                )
                triggers.append(trigger)
            
            elif schedule_type == 'date':
                # 指定时间调度
                date_config = config.get('date', {})
                run_date = date_config.get('run_date')
                if run_date:
                    trigger = DateTrigger(run_date=run_date)
                    triggers.append(trigger)
                else:
                    self.logger.error("日期调度配置缺少run_date字段")
                    return None
            
            else:
                self.logger.error(f"不支持的调度类型: {schedule_type}")
                return None
            
            return triggers
                
        except Exception as e:
            self.logger.error(f"解析调度配置失败: {e}")
            return None
    
    def _job_listener(self, event):
        """任务执行事件监听器"""
        try:
            if event.code == EVENT_JOB_EXECUTED:
                # 任务执行成功
                task_id = event.job_id
                self.logger.info(f"任务执行成功: {task_id}")
                
                # 更新任务状态
                if task_id in self.task_status:
                    self.task_status[task_id]['status'] = 'completed'
                    self.task_status[task_id]['last_run_time'] = datetime.now().isoformat()
                    self.task_status[task_id]['next_run_time'] = event.scheduled_run_time.isoformat()
                
            elif event.code == EVENT_JOB_ERROR:
                # 任务执行失败
                task_id = event.job_id
                error_msg = str(event.exception)
                self.logger.error(f"任务执行失败: {task_id}, 错误: {error_msg}")
                
                # 更新任务状态
                if task_id in self.task_status:
                    self.task_status[task_id]['status'] = 'failed'
                    self.task_status[task_id]['last_error'] = error_msg
                    self.task_status[task_id]['last_error_time'] = datetime.now().isoformat()
                
        except Exception as e:
            self.logger.error(f"处理任务事件失败: {e}")
    
    def is_running(self) -> bool:
        """检查调度器是否正在运行"""
        return self.scheduler.running if hasattr(self, 'scheduler') else False
    
    def get_stats(self) -> Dict[str, Any]:
        """获取调度器统计信息"""
        try:
            if not hasattr(self, 'scheduler'):
                return {}
            
            return {
                'running': self.scheduler.running,
                'job_count': len(self.scheduler.get_jobs()),
                'running_tasks': len(self.get_running_tasks()),
                'max_workers': self.max_workers,
                'scheduler_info': {
                    'executors': list(self.scheduler.executors.keys()) if hasattr(self.scheduler, 'executors') else []
                }
            }
            
        except Exception as e:
            self.logger.error(f"获取调度器统计信息失败: {e}")
            return {}

