# -----------------------------
# 题目：实现分布式调度器。
# 描述：支持任务调度、故障转移、负载均衡。
# -----------------------------

import time
import threading
import random
import hashlib
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from queue import PriorityQueue
from datetime import datetime

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    LOW = 3
    NORMAL = 2
    HIGH = 1
    CRITICAL = 0

@dataclass
class Task:
    task_id: str
    name: str
    func: Callable
    args: tuple = ()
    kwargs: Dict = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    scheduled_time: Optional[float] = None
    max_retries: int = 3
    retry_count: int = 0
    timeout: float = 300.0
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Any = None
    error: Optional[str] = None
    assigned_worker: Optional[str] = None
    
    def __lt__(self, other):
        return (self.priority.value, self.created_at) < (other.priority.value, other.created_at)

@dataclass
class Worker:
    worker_id: str
    host: str
    port: int
    capacity: int = 10
    current_load: int = 0
    status: str = "idle"
    last_heartbeat: float = field(default_factory=time.time)
    completed_tasks: int = 0
    failed_tasks: int = 0

class LoadBalancer:
    def __init__(self):
        self.strategy = "least_loaded"
    
    def select_worker(self, workers: List[Worker], task: Task) -> Optional[Worker]:
        available = [w for w in workers if w.current_load < w.capacity]
        
        if not available:
            return None
        
        if self.strategy == "least_loaded":
            return min(available, key=lambda w: w.current_load)
        elif self.strategy == "round_robin":
            return random.choice(available)
        elif self.strategy == "random":
            return random.choice(available)
        else:
            return available[0]

class TaskScheduler:
    def __init__(self):
        self.workers: Dict[str, Worker] = {}
        self.tasks: Dict[str, Task] = {}
        self.task_queue: PriorityQueue = PriorityQueue()
        self.running_tasks: Dict[str, Task] = {}
        self.load_balancer = LoadBalancer()
        self._lock = threading.RLock()
        self._running = False
        self._scheduler_thread: Optional[threading.Thread] = None
        self._task_counter = 0
    
    def register_worker(self, worker_id: str, host: str, port: int, capacity: int = 10):
        with self._lock:
            self.workers[worker_id] = Worker(
                worker_id=worker_id,
                host=host,
                port=port,
                capacity=capacity
            )
    
    def unregister_worker(self, worker_id: str):
        with self._lock:
            self.workers.pop(worker_id, None)
    
    def submit_task(
        self,
        name: str,
        func: Callable,
        args: tuple = (),
        kwargs: Dict = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        scheduled_time: float = None,
        max_retries: int = 3
    ) -> str:
        with self._lock:
            self._task_counter += 1
            task_id = f"task-{int(time.time())}-{self._task_counter}"
        
        task = Task(
            task_id=task_id,
            name=name,
            func=func,
            args=args,
            kwargs=kwargs or {},
            priority=priority,
            scheduled_time=scheduled_time,
            max_retries=max_retries
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
            self._check_timeouts()
            self._check_worker_health()
            time.sleep(0.1)
    
    def _process_tasks(self):
        while not self.task_queue.empty():
            try:
                task = self.task_queue.get_nowait()
                
                if task.scheduled_time and time.time() < task.scheduled_time:
                    self.task_queue.put(task)
                    break
                
                worker = self.load_balancer.select_worker(
                    list(self.workers.values()), task
                )
                
                if worker:
                    self._assign_task(task, worker)
                else:
                    self.task_queue.put(task)
                    break
            
            except:
                break
    
    def _assign_task(self, task: Task, worker: Worker):
        with self._lock:
            task.status = TaskStatus.RUNNING
            task.started_at = time.time()
            task.assigned_worker = worker.worker_id
            worker.current_load += 1
            self.running_tasks[task.task_id] = task
        
        threading.Thread(
            target=self._execute_task,
            args=(task, worker)
        ).start()
    
    def _execute_task(self, task: Task, worker: Worker):
        try:
            result = task.func(*task.args, **task.kwargs)
            
            with self._lock:
                task.status = TaskStatus.COMPLETED
                task.result = result
                task.completed_at = time.time()
                worker.current_load -= 1
                worker.completed_tasks += 1
                self.running_tasks.pop(task.task_id, None)
        
        except Exception as e:
            with self._lock:
                task.error = str(e)
                task.retry_count += 1
                
                if task.retry_count < task.max_retries:
                    task.status = TaskStatus.PENDING
                    self.task_queue.put(task)
                else:
                    task.status = TaskStatus.FAILED
                    worker.failed_tasks += 1
                
                worker.current_load -= 1
                self.running_tasks.pop(task.task_id, None)
    
    def _check_timeouts(self):
        now = time.time()
        with self._lock:
            for task in list(self.running_tasks.values()):
                if task.started_at and now - task.started_at > task.timeout:
                    task.status = TaskStatus.FAILED
                    task.error = "Task timeout"
                    
                    if task.assigned_worker:
                        worker = self.workers.get(task.assigned_worker)
                        if worker:
                            worker.current_load -= 1
                            worker.failed_tasks += 1
                    
                    self.running_tasks.pop(task.task_id, None)
    
    def _check_worker_health(self):
        now = time.time()
        with self._lock:
            for worker in list(self.workers.values()):
                if now - worker.last_heartbeat > 30:
                    self._handle_worker_failure(worker)
    
    def _handle_worker_failure(self, worker: Worker):
        with self._lock:
            for task in list(self.running_tasks.values()):
                if task.assigned_worker == worker.worker_id:
                    task.status = TaskStatus.PENDING
                    task.assigned_worker = None
                    task.retry_count += 1
                    self.task_queue.put(task)
                    self.running_tasks.pop(task.task_id, None)
            
            self.workers.pop(worker.worker_id, None)
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        task = self.tasks.get(task_id)
        if task:
            return {
                'task_id': task.task_id,
                'name': task.name,
                'status': task.status.value,
                'result': task.result,
                'error': task.error
            }
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            return {
                'total_tasks': len(self.tasks),
                'pending_tasks': self.task_queue.qsize(),
                'running_tasks': len(self.running_tasks),
                'workers': {
                    wid: {
                        'load': w.current_load,
                        'capacity': w.capacity,
                        'completed': w.completed_tasks,
                        'failed': w.failed_tasks
                    }
                    for wid, w in self.workers.items()
                }
            }

def main():
    scheduler = TaskScheduler()
    
    scheduler.register_worker("worker-1", "localhost", 8001, capacity=3)
    scheduler.register_worker("worker-2", "localhost", 8002, capacity=3)
    
    scheduler.start()
    
    def process_order(order_id: str):
        time.sleep(0.5)
        return f"订单 {order_id} 处理完成"
    
    print("提交任务...")
    for i in range(6):
        task_id = scheduler.submit_task(
            f"process-order-{i}",
            process_order,
            args=(f"ORD-{i}",),
            priority=TaskPriority.NORMAL
        )
        print(f"  提交任务: {task_id}")
    
    time.sleep(3)
    
    print("\n调度器统计:")
    stats = scheduler.get_stats()
    print(f"  总任务: {stats['total_tasks']}")
    print(f"  运行中: {stats['running_tasks']}")
    print(f"  工作节点: {stats['workers']}")
    
    scheduler.stop()

if __name__ == "__main__":
    main()
