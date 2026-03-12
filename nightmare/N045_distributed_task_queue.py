# -----------------------------
# 题目：实现分布式任务队列。
# 描述：支持任务分发、优先级队列、延迟任务。
# -----------------------------

import time
import threading
import heapq
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from queue import Queue, Empty
from collections import defaultdict

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    DELAYED = "delayed"

class TaskPriority(Enum):
    LOW = 3
    NORMAL = 2
    HIGH = 1
    CRITICAL = 0

@dataclass(order=True)
class Task:
    task_id: str
    name: str
    handler: str
    args: tuple = ()
    kwargs: Dict = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    delay: float = 0
    max_retries: int = 3
    retry_count: int = 0
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Any = None
    error: Optional[str] = None
    
    def __lt__(self, other):
        return (self.priority.value, self.created_at) < (other.priority.value, other.created_at)

class TaskQueue:
    def __init__(self):
        self._queue: List[Task] = []
        self._delayed: List[Task] = []
        self._lock = threading.Lock()
    
    def push(self, task: Task):
        with self._lock:
            if task.delay > 0:
                heapq.heappush(self._delayed, task)
            else:
                heapq.heappush(self._queue, task)
    
    def pop(self) -> Optional[Task]:
        with self._lock:
            self._process_delayed()
            
            if self._queue:
                return heapq.heappop(self._queue)
            return None
    
    def _process_delayed(self):
        now = time.time()
        ready = []
        
        for task in self._delayed:
            if task.created_at + task.delay <= now:
                ready.append(task)
        
        for task in ready:
            self._delayed.remove(task)
            heapq.heappush(self._queue, task)
    
    def size(self) -> int:
        with self._lock:
            return len(self._queue) + len(self._delayed)

class TaskRegistry:
    def __init__(self):
        self._handlers: Dict[str, Callable] = {}
    
    def register(self, name: str, handler: Callable):
        self._handlers[name] = handler
    
    def get(self, name: str) -> Optional[Callable]:
        return self._handlers.get(name)

class Worker:
    def __init__(self, worker_id: str, registry: TaskRegistry):
        self.worker_id = worker_id
        self.registry = registry
        self.status = "idle"
        self.current_task: Optional[str] = None
        self.completed_tasks = 0
        self.failed_tasks = 0

class DistributedTaskQueue:
    def __init__(self, num_workers: int = 4):
        self.queue = TaskQueue()
        self.registry = TaskRegistry()
        self.workers: Dict[str, Worker] = {}
        self.tasks: Dict[str, Task] = {}
        self._running = False
        self._worker_threads: List[threading.Thread] = []
        self._task_counter = 0
        self._lock = threading.Lock()
        
        for i in range(num_workers):
            worker_id = f"worker-{i}"
            self.workers[worker_id] = Worker(worker_id, self.registry)
    
    def register_handler(self, name: str, handler: Callable):
        self.registry.register(name, handler)
    
    def submit(
        self,
        name: str,
        handler: str,
        args: tuple = (),
        kwargs: Dict = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        delay: float = 0,
        max_retries: int = 3
    ) -> str:
        with self._lock:
            self._task_counter += 1
            task_id = f"task-{int(time.time())}-{self._task_counter}"
        
        task = Task(
            task_id=task_id,
            name=name,
            handler=handler,
            args=args,
            kwargs=kwargs or {},
            priority=priority,
            delay=delay,
            max_retries=max_retries
        )
        
        with self._lock:
            self.tasks[task_id] = task
        
        self.queue.push(task)
        
        return task_id
    
    def start(self):
        self._running = True
        
        for worker_id, worker in self.workers.items():
            thread = threading.Thread(target=self._worker_loop, args=(worker,))
            thread.daemon = True
            thread.start()
            self._worker_threads.append(thread)
    
    def stop(self):
        self._running = False
    
    def _worker_loop(self, worker: Worker):
        while self._running:
            task = self.queue.pop()
            
            if task:
                worker.status = "busy"
                worker.current_task = task.task_id
                
                self._execute_task(task, worker)
                
                worker.status = "idle"
                worker.current_task = None
            else:
                time.sleep(0.1)
    
    def _execute_task(self, task: Task, worker: Worker):
        task.status = TaskStatus.RUNNING
        task.started_at = time.time()
        
        handler = self.registry.get(task.handler)
        
        if not handler:
            task.status = TaskStatus.FAILED
            task.error = f"Handler not found: {task.handler}"
            worker.failed_tasks += 1
            return
        
        try:
            result = handler(*task.args, **task.kwargs)
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = time.time()
            worker.completed_tasks += 1
        except Exception as e:
            task.retry_count += 1
            task.error = str(e)
            
            if task.retry_count < task.max_retries:
                task.status = TaskStatus.PENDING
                self.queue.push(task)
            else:
                task.status = TaskStatus.FAILED
                task.completed_at = time.time()
                worker.failed_tasks += 1
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        task = self.tasks.get(task_id)
        if task:
            return {
                'task_id': task.task_id,
                'name': task.name,
                'status': task.status.value,
                'result': task.result,
                'error': task.error,
                'retry_count': task.retry_count
            }
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'queue_size': self.queue.size(),
            'total_tasks': len(self.tasks),
            'workers': {
                wid: {
                    'status': w.status,
                    'completed': w.completed_tasks,
                    'failed': w.failed_tasks
                }
                for wid, w in self.workers.items()
            }
        }

def main():
    dtq = DistributedTaskQueue(num_workers=3)
    
    dtq.register_handler("add", lambda a, b: a + b)
    dtq.register_handler("multiply", lambda a, b: a * b)
    dtq.register_handler("slow", lambda: time.sleep(0.5) or "done")
    
    dtq.start()
    
    print("提交任务...")
    task1 = dtq.submit("加法", "add", args=(1, 2), priority=TaskPriority.HIGH)
    task2 = dtq.submit("乘法", "multiply", args=(3, 4), priority=TaskPriority.NORMAL)
    task3 = dtq.submit("慢任务", "slow", priority=TaskPriority.LOW)
    task4 = dtq.submit("延迟任务", "add", args=(5, 6), delay=2.0)
    
    print(f"  提交: {task1}, {task2}, {task3}, {task4}")
    
    time.sleep(3)
    
    print("\n任务状态:")
    for task_id in [task1, task2, task3, task4]:
        status = dtq.get_task_status(task_id)
        if status:
            print(f"  {status['name']}: {status['status']}, 结果={status['result']}")
    
    print("\n队列统计:")
    stats = dtq.get_stats()
    print(f"  队列大小: {stats['queue_size']}")
    print(f"  工作节点: {stats['workers']}")
    
    dtq.stop()

if __name__ == "__main__":
    main()
