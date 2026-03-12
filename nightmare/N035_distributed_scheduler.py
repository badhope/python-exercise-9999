# -----------------------------
# 题目：实现分布式任务调度器。
# 描述：支持定时任务、任务分片、故障转移。
# -----------------------------

import time
import threading
import random
import hashlib
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from queue import PriorityQueue
from datetime import datetime, timedelta

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ScheduledTask:
    task_id: str
    name: str
    func: Callable
    args: tuple = ()
    kwargs: Dict = field(default_factory=dict)
    cron: Optional[str] = None
    next_run: Optional[float] = None
    interval: Optional[float] = None
    status: TaskStatus = TaskStatus.PENDING
    max_retries: int = 3
    retry_count: int = 0
    last_run: Optional[float] = None
    last_result: Any = None
    created_at: float = field(default_factory=time.time)
    
    def __lt__(self, other):
        return (self.next_run or 0) < (other.next_run or 0)

@dataclass
class WorkerNode:
    node_id: str
    host: str
    port: int
    capacity: int = 10
    current_load: int = 0
    status: str = "online"
    last_heartbeat: float = field(default_factory=time.time)
    shards: List[int] = field(default_factory=list)

class CronParser:
    @staticmethod
    def parse(cron_expr: str) -> float:
        now = time.time()
        parts = cron_expr.split()
        
        if len(parts) != 5:
            return now + 60
        
        minute, hour, day, month, weekday = parts
        
        return now + 60

class TaskSharding:
    def __init__(self, total_shards: int = 16):
        self.total_shards = total_shards
        self._shard_assignments: Dict[int, str] = {}
    
    def get_shard(self, task_id: str) -> int:
        hash_val = int(hashlib.md5(task_id.encode()).hexdigest(), 16)
        return hash_val % self.total_shards
    
    def assign_shards(self, node_id: str, shards: List[int]):
        for shard in shards:
            self._shard_assignments[shard] = node_id
    
    def get_node_for_task(self, task_id: str) -> Optional[str]:
        shard = self.get_shard(task_id)
        return self._shard_assignments.get(shard)

class DistributedScheduler:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.tasks: Dict[str, ScheduledTask] = {}
        self.task_queue: PriorityQueue = PriorityQueue()
        self.workers: Dict[str, WorkerNode] = {}
        self.sharding = TaskSharding()
        self._running = False
        self._scheduler_thread: Optional[threading.Thread] = None
        self._heartbeat_thread: Optional[threading.Thread] = None
        self._task_counter = 0
        self._lock = threading.RLock()
    
    def register_worker(self, worker: WorkerNode):
        with self._lock:
            self.workers[worker.node_id] = worker
            
            shards_per_worker = self.sharding.total_shards // (len(self.workers) + 1)
            
            for i, w in enumerate(self.workers.values()):
                start = i * shards_per_worker
                end = start + shards_per_worker
                w.shards = list(range(start, end))
                self.sharding.assign_shards(w.node_id, w.shards)
    
    def submit_task(
        self,
        name: str,
        func: Callable,
        args: tuple = (),
        kwargs: Dict = None,
        cron: str = None,
        interval: float = None,
        start_time: float = None
    ) -> str:
        with self._lock:
            self._task_counter += 1
            task_id = f"task-{int(time.time())}-{self._task_counter}"
        
        next_run = start_time or time.time()
        
        if cron:
            next_run = CronParser.parse(cron)
        elif interval:
            next_run = time.time()
        
        task = ScheduledTask(
            task_id=task_id,
            name=name,
            func=func,
            args=args,
            kwargs=kwargs or {},
            cron=cron,
            interval=interval,
            next_run=next_run
        )
        
        with self._lock:
            self.tasks[task_id] = task
            self.task_queue.put(task)
        
        return task_id
    
    def start(self):
        self._running = True
        self._scheduler_thread = threading.Thread(target=self._schedule_loop)
        self._scheduler_thread.daemon = True
        self._scheduler_thread.start()
    
    def stop(self):
        self._running = False
        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=5.0)
    
    def _schedule_loop(self):
        while self._running:
            self._process_tasks()
            time.sleep(0.1)
    
    def _process_tasks(self):
        now = time.time()
        
        temp_tasks = []
        
        while not self.task_queue.empty():
            try:
                task = self.task_queue.get_nowait()
                
                if task.next_run and task.next_run <= now:
                    self._execute_task(task)
                    
                    if task.interval:
                        task.next_run = now + task.interval
                        task.status = TaskStatus.PENDING
                        temp_tasks.append(task)
                    elif task.cron:
                        task.next_run = CronParser.parse(task.cron)
                        task.status = TaskStatus.PENDING
                        temp_tasks.append(task)
                else:
                    temp_tasks.append(task)
            
            except:
                break
        
        for task in temp_tasks:
            self.task_queue.put(task)
    
    def _execute_task(self, task: ScheduledTask):
        assigned_node = self.sharding.get_node_for_task(task.task_id)
        
        if assigned_node and assigned_node != self.node_id:
            return
        
        task.status = TaskStatus.RUNNING
        task.last_run = time.time()
        
        try:
            result = task.func(*task.args, **task.kwargs)
            task.status = TaskStatus.COMPLETED
            task.last_result = result
            task.retry_count = 0
        except Exception as e:
            task.retry_count += 1
            
            if task.retry_count >= task.max_retries:
                task.status = TaskStatus.FAILED
                task.last_result = str(e)
            else:
                task.status = TaskStatus.PENDING
    
    def cancel_task(self, task_id: str) -> bool:
        with self._lock:
            task = self.tasks.get(task_id)
            if task:
                task.status = TaskStatus.CANCELLED
                return True
            return False
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        task = self.tasks.get(task_id)
        if task:
            return {
                'task_id': task.task_id,
                'name': task.name,
                'status': task.status.value,
                'next_run': task.next_run,
                'last_run': task.last_run,
                'retry_count': task.retry_count
            }
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            status_counts = {}
            for task in self.tasks.values():
                status = task.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
            
            return {
                'node_id': self.node_id,
                'total_tasks': len(self.tasks),
                'queue_size': self.task_queue.qsize(),
                'workers': len(self.workers),
                'status_counts': status_counts
            }

def main():
    scheduler = DistributedScheduler("scheduler-1")
    
    scheduler.register_worker(WorkerNode("worker-1", "localhost", 8001))
    scheduler.register_worker(WorkerNode("worker-2", "localhost", 8002))
    
    scheduler.start()
    
    def hello_task(name: str):
        print(f"  执行任务: Hello, {name}!")
        return f"Greeted {name}"
    
    def periodic_task():
        print(f"  周期任务执行: {datetime.now().isoformat()}")
        return "done"
    
    print("提交任务...")
    task1 = scheduler.submit_task("greeting", hello_task, args=("World",))
    print(f"  提交一次性任务: {task1}")
    
    task2 = scheduler.submit_task("periodic", periodic_task, interval=1.0)
    print(f"  提交周期任务: {task2}")
    
    print("\n等待任务执行...")
    time.sleep(3)
    
    print("\n任务状态:")
    print(f"  {scheduler.get_task_status(task1)}")
    print(f"  {scheduler.get_task_status(task2)}")
    
    print("\n调度器统计:")
    print(f"  {scheduler.get_stats()}")
    
    scheduler.cancel_task(task2)
    print(f"\n取消周期任务: {task2}")
    
    scheduler.stop()

if __name__ == "__main__":
    main()
