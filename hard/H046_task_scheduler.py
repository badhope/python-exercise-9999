# -----------------------------
# 题目：实现简单的任务调度系统。
# 描述：管理定时任务、执行、日志等。
# -----------------------------

from datetime import datetime, timedelta
from enum import Enum

class TaskStatus(Enum):
    PENDING = "待执行"
    RUNNING = "执行中"
    COMPLETED = "已完成"
    FAILED = "失败"
    CANCELLED = "已取消"

class Task:
    def __init__(self, task_id, name, command, schedule_time):
        self.id = task_id
        self.name = name
        self.command = command
        self.schedule_time = schedule_time
        self.status = TaskStatus.PENDING
        self.priority = 5
        self.retry_count = 0
        self.max_retries = 3
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.result = None
        self.error = None
    
    def execute(self):
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.now()
        try:
            self.result = f"执行命令: {self.command}"
            self.status = TaskStatus.COMPLETED
            self.completed_at = datetime.now()
            return True
        except Exception as e:
            self.error = str(e)
            self.status = TaskStatus.FAILED
            return False
    
    def get_duration(self):
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

class TaskLog:
    def __init__(self, log_id, task_id, message, level="INFO"):
        self.id = log_id
        self.task_id = task_id
        self.message = message
        self.level = level
        self.timestamp = datetime.now()

class Scheduler:
    def __init__(self):
        self.tasks = {}
        self.logs = []
        self.next_task_id = 1
        self.next_log_id = 1
        self.running = False
    
    def add_task(self, name, command, schedule_time, priority=5):
        task = Task(self.next_task_id, name, command, schedule_time)
        task.priority = priority
        self.tasks[self.next_task_id] = task
        self._log(self.next_task_id, f"任务创建: {name}", "INFO")
        self.next_task_id += 1
        return task.id
    
    def cancel_task(self, task_id):
        task = self.tasks.get(task_id)
        if task and task.status == TaskStatus.PENDING:
            task.status = TaskStatus.CANCELLED
            self._log(task_id, "任务已取消", "INFO")
            return True
        return False
    
    def retry_task(self, task_id):
        task = self.tasks.get(task_id)
        if task and task.status == TaskStatus.FAILED and task.retry_count < task.max_retries:
            task.retry_count += 1
            task.status = TaskStatus.PENDING
            self._log(task_id, f"任务重试 ({task.retry_count}/{task.max_retries})", "INFO")
            return True
        return False
    
    def run_pending(self):
        now = datetime.now()
        pending_tasks = [
            t for t in self.tasks.values()
            if t.status == TaskStatus.PENDING and t.schedule_time <= now
        ]
        pending_tasks.sort(key=lambda x: x.priority)
        
        for task in pending_tasks:
            self._log(task.id, f"开始执行任务: {task.name}", "INFO")
            success = task.execute()
            if success:
                self._log(task.id, f"任务完成，耗时: {task.get_duration():.2f}秒", "INFO")
            else:
                self._log(task.id, f"任务失败: {task.error}", "ERROR")
    
    def _log(self, task_id, message, level="INFO"):
        log = TaskLog(self.next_log_id, task_id, message, level)
        self.logs.append(log)
        self.next_log_id += 1
    
    def get_task_logs(self, task_id):
        return [log for log in self.logs if log.task_id == task_id]
    
    def get_pending_tasks(self):
        return [t for t in self.tasks.values() if t.status == TaskStatus.PENDING]
    
    def get_running_tasks(self):
        return [t for t in self.tasks.values() if t.status == TaskStatus.RUNNING]
    
    def get_completed_tasks(self):
        return [t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED]
    
    def get_failed_tasks(self):
        return [t for t in self.tasks.values() if t.status == TaskStatus.FAILED]
    
    def get_task_info(self, task_id):
        task = self.tasks.get(task_id)
        if task:
            return {
                'id': task.id,
                'name': task.name,
                'status': task.status.value,
                'schedule_time': task.schedule_time.strftime('%Y-%m-%d %H:%M:%S'),
                'priority': task.priority,
                'retry_count': task.retry_count,
                'duration': task.get_duration()
            }
        return None
    
    def get_stats(self):
        return {
            'total': len(self.tasks),
            'pending': len(self.get_pending_tasks()),
            'running': len(self.get_running_tasks()),
            'completed': len(self.get_completed_tasks()),
            'failed': len(self.get_failed_tasks())
        }

def main():
    scheduler = Scheduler()
    
    now = datetime.now()
    
    t1 = scheduler.add_task("数据备份", "backup.sh", now + timedelta(seconds=1), priority=1)
    t2 = scheduler.add_task("日志清理", "clean_logs.sh", now + timedelta(seconds=2), priority=3)
    t3 = scheduler.add_task("报告生成", "generate_report.sh", now + timedelta(seconds=3), priority=2)
    
    import time
    time.sleep(4)
    scheduler.run_pending()
    
    print("任务调度统计:")
    stats = scheduler.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print(f"\n任务{t1}信息:")
    info = scheduler.get_task_info(t1)
    for key, value in info.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
