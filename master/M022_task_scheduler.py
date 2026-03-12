# -----------------------------
# 题目：实现任务调度器。
# 描述：支持定时任务、延迟任务、周期任务。
# -----------------------------

import time
import threading
import heapq
from typing import Callable, Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass(order=True)
class ScheduledTask:
    scheduled_time: float
    task_id: str = field(compare=False)
    func: Callable = field(compare=False)
    args: tuple = field(compare=False, default=())
    kwargs: dict = field(compare=False, default_factory=dict)
    interval: Optional[float] = field(compare=False, default=None)
    status: TaskStatus = field(compare=False, default=TaskStatus.PENDING)
    result: Any = field(compare=False, default=None)
    error: Optional[str] = field(compare=False, default=None)
    created_at: float = field(compare=False, default_factory=time.time)
    execution_count: int = field(compare=False, default=0)

class TaskScheduler:
    def __init__(self, max_workers: int = 4):
        self.tasks: Dict[str, ScheduledTask] = {}
        self.task_queue: List[ScheduledTask] = []
        self._lock = threading.RLock()
        self._running = False
        self._max_workers = max_workers
        self._workers: List[threading.Thread] = []
        self._scheduler_thread: Optional[threading.Thread] = None
        self._task_counter = 0
    
    def _generate_task_id(self) -> str:
        with self._lock:
            self._task_counter += 1
            return f"task-{int(time.time())}-{self._task_counter}"
    
    def schedule(
        self,
        func: Callable,
        args: tuple = (),
        kwargs: dict = None,
        delay: float = 0,
        scheduled_time: float = None
    ) -> str:
        task_id = self._generate_task_id()
        
        if scheduled_time is None:
            scheduled_time = time.time() + delay
        
        task = ScheduledTask(
            scheduled_time=scheduled_time,
            task_id=task_id,
            func=func,
            args=args,
            kwargs=kwargs or {}
        )
        
        with self._lock:
            self.tasks[task_id] = task
            heapq.heappush(self.task_queue, task)
        
        return task_id
    
    def schedule_periodic(
        self,
        func: Callable,
        interval: float,
        args: tuple = (),
        kwargs: dict = None,
        initial_delay: float = 0
    ) -> str:
        task_id = self._generate_task_id()
        scheduled_time = time.time() + initial_delay
        
        task = ScheduledTask(
            scheduled_time=scheduled_time,
            task_id=task_id,
            func=func,
            args=args,
            kwargs=kwargs or {},
            interval=interval
        )
        
        with self._lock:
            self.tasks[task_id] = task
            heapq.heappush(self.task_queue, task)
        
        return task_id
    
    def schedule_cron(
        self,
        func: Callable,
        cron_expr: str,
        args: tuple = (),
        kwargs: dict = None
    ) -> str:
        next_time = self._parse_cron(cron_expr)
        return self.schedule(func, args, kwargs, scheduled_time=next_time)
    
    def _parse_cron(self, cron_expr: str) -> float:
        parts = cron_expr.split()
        if len(parts) != 5:
            raise ValueError("无效的cron表达式")
        
        now = datetime.now()
        minute, hour, day, month, weekday = parts
        
        next_time = now + timedelta(minutes=1)
        return next_time.timestamp()
    
    def cancel(self, task_id: str) -> bool:
        with self._lock:
            if task_id in self.tasks:
                self.tasks[task_id].status = TaskStatus.CANCELLED
                return True
            return False
    
    def get_task(self, task_id: str) -> Optional[ScheduledTask]:
        return self.tasks.get(task_id)
    
    def start(self):
        self._running = True
        
        self._scheduler_thread = threading.Thread(target=self._scheduler_loop)
        self._scheduler_thread.daemon = True
        self._scheduler_thread.start()
        
        for i in range(self._max_workers):
            worker = threading.Thread(target=self._worker_loop, args=(i,))
            worker.daemon = True
            worker.start()
            self._workers.append(worker)
    
    def stop(self):
        self._running = False
        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=2.0)
        for worker in self._workers:
            worker.join(timeout=1.0)
        self._workers.clear()
    
    def _scheduler_loop(self):
        while self._running:
            self._check_tasks()
            time.sleep(0.1)
    
    def _check_tasks(self):
        now = time.time()
        
        with self._lock:
            while self.task_queue and self.task_queue[0].scheduled_time <= now:
                task = heapq.heappop(self.task_queue)
                
                if task.status == TaskStatus.CANCELLED:
                    continue
                
                task.status = TaskStatus.RUNNING
                threading.Thread(target=self._execute_task, args=(task,)).start()
    
    def _execute_task(self, task: ScheduledTask):
        try:
            task.result = task.func(*task.args, **task.kwargs)
            task.status = TaskStatus.COMPLETED
            task.execution_count += 1
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
        
        if task.interval and task.status == TaskStatus.COMPLETED:
            task.scheduled_time = time.time() + task.interval
            task.status = TaskStatus.PENDING
            with self._lock:
                heapq.heappush(self.task_queue, task)
    
    def _worker_loop(self, worker_id: int):
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            status_counts = {}
            for task in self.tasks.values():
                status = task.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
            
            return {
                'total_tasks': len(self.tasks),
                'queue_size': len(self.task_queue),
                'status_counts': status_counts
            }

def main():
    scheduler = TaskScheduler(max_workers=2)
    scheduler.start()
    
    results = []
    
    def simple_task(name: str):
        result = f"任务 {name} 在 {datetime.now().strftime('%H:%M:%S')} 执行"
        results.append(result)
        print(result)
        return result
    
    def periodic_task():
        print(f"周期任务执行于 {datetime.now().strftime('%H:%M:%S')}")
        return "periodic"
    
    task1 = scheduler.schedule(simple_task, args=("一次性任务",), delay=1.0)
    task2 = scheduler.schedule_periodic(periodic_task, interval=2.0, initial_delay=0.5)
    task3 = scheduler.schedule(simple_task, args=("延迟任务",), delay=3.0)
    
    print(f"调度任务: {task1}, {task2}, {task3}")
    
    time.sleep(6)
    
    scheduler.cancel(task2)
    print(f"取消周期任务: {task2}")
    
    time.sleep(1)
    
    print(f"\n统计: {scheduler.get_stats()}")
    scheduler.stop()

if __name__ == "__main__":
    main()
