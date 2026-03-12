# -----------------------------
# 题目：实现异步任务执行器。
# 描述：支持任务提交、并发执行、结果获取。
# -----------------------------

import time
import threading
import uuid
from typing import Callable, Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import Future
from queue import Queue

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class TaskResult:
    task_id: str
    status: TaskStatus
    result: Any = None
    error: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    
    @property
    def duration(self) -> Optional[float]:
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None

@dataclass
class Task:
    task_id: str
    func: Callable
    args: tuple
    kwargs: dict
    future: Future = field(default_factory=Future)
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[TaskResult] = None
    created_at: float = field(default_factory=time.time)

class AsyncTaskExecutor:
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self._task_queue: Queue = Queue()
        self._workers: List[threading.Thread] = []
        self._tasks: Dict[str, Task] = {}
        self._running = False
        self._task_counter = 0
        self._lock = threading.Lock()
    
    def _generate_task_id(self) -> str:
        with self._lock:
            self._task_counter += 1
            return f"task-{int(time.time())}-{self._task_counter}"
    
    def submit(self, func: Callable, *args, **kwargs) -> str:
        task_id = self._generate_task_id()
        
        task = Task(
            task_id=task_id,
            func=func,
            args=args,
            kwargs=kwargs
        )
        
        with self._lock:
            self._tasks[task_id] = task
        
        self._task_queue.put(task)
        
        return task_id
    
    def map(self, func: Callable, items: List[Any]) -> List[str]:
        task_ids = []
        for item in items:
            if isinstance(item, (tuple, list)):
                task_id = self.submit(func, *item)
            else:
                task_id = self.submit(func, item)
            task_ids.append(task_id)
        return task_ids
    
    def get_result(self, task_id: str, timeout: float = None) -> Optional[TaskResult]:
        task = self._tasks.get(task_id)
        if not task:
            return None
        
        try:
            task.future.result(timeout=timeout)
        except Exception:
            pass
        
        return task.result
    
    def wait_all(self, task_ids: List[str], timeout: float = None) -> Dict[str, TaskResult]:
        results = {}
        start_time = time.time()
        
        for task_id in task_ids:
            remaining_timeout = None
            if timeout:
                elapsed = time.time() - start_time
                remaining_timeout = max(0, timeout - elapsed)
            
            results[task_id] = self.get_result(task_id, remaining_timeout)
        
        return results
    
    def cancel(self, task_id: str) -> bool:
        task = self._tasks.get(task_id)
        if task and task.status == TaskStatus.PENDING:
            task.status = TaskStatus.CANCELLED
            task.future.cancel()
            return True
        return False
    
    def start(self):
        self._running = True
        
        for i in range(self.max_workers):
            worker = threading.Thread(target=self._worker_loop, args=(i,))
            worker.daemon = True
            worker.start()
            self._workers.append(worker)
    
    def stop(self):
        self._running = False
        
        for _ in range(self.max_workers):
            self._task_queue.put(None)
        
        for worker in self._workers:
            worker.join(timeout=5.0)
        
        self._workers.clear()
    
    def _worker_loop(self, worker_id: int):
        while self._running:
            try:
                task = self._task_queue.get(timeout=1.0)
                
                if task is None:
                    continue
                
                if task.status == TaskStatus.CANCELLED:
                    continue
                
                self._execute_task(task)
            
            except Exception:
                pass
    
    def _execute_task(self, task: Task):
        task.status = TaskStatus.RUNNING
        start_time = time.time()
        
        try:
            result = task.func(*task.args, **task.kwargs)
            
            task.result = TaskResult(
                task_id=task.task_id,
                status=TaskStatus.COMPLETED,
                result=result,
                start_time=start_time,
                end_time=time.time()
            )
            task.future.set_result(result)
        
        except Exception as e:
            task.result = TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error=str(e),
                start_time=start_time,
                end_time=time.time()
            )
            task.future.set_exception(e)
        
        task.status = task.result.status
    
    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            status_counts = {}
            for task in self._tasks.values():
                status = task.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
            
            return {
                'total_tasks': len(self._tasks),
                'queue_size': self._task_queue.qsize(),
                'workers': self.max_workers,
                'status_counts': status_counts
            }

def async_task(executor: AsyncTaskExecutor):
    def decorator(func):
        def wrapper(*args, **kwargs):
            return executor.submit(func, *args, **kwargs)
        return wrapper
    return decorator

def main():
    executor = AsyncTaskExecutor(max_workers=3)
    executor.start()
    
    def slow_task(name: str, duration: float) -> str:
        time.sleep(duration)
        return f"{name} 完成 (耗时 {duration}s)"
    
    def failing_task(name: str) -> str:
        raise ValueError(f"{name} 任务失败")
    
    task1 = executor.submit(slow_task, "任务A", 0.5)
    task2 = executor.submit(slow_task, "任务B", 0.3)
    task3 = executor.submit(failing_task, "任务C")
    
    print(f"提交任务: {task1}, {task2}, {task3}")
    
    results = executor.wait_all([task1, task2, task3])
    
    for task_id, result in results.items():
        if result:
            print(f"任务 {task_id}:")
            print(f"  状态: {result.status.value}")
            print(f"  结果: {result.result}")
            print(f"  错误: {result.error}")
            print(f"  耗时: {result.duration:.3f}s")
    
    print(f"\n执行器统计: {executor.get_stats()}")
    
    executor.stop()

if __name__ == "__main__":
    main()
