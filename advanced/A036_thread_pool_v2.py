# -----------------------------
# 题目：实现简单的线程池。
# -----------------------------

import threading
import queue
import time
from typing import Callable, Any, List, Optional
from dataclasses import dataclass
from concurrent.futures import Future
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Task:
    id: int
    func: Callable
    args: tuple
    kwargs: dict
    future: Future
    status: TaskStatus = TaskStatus.PENDING

class Worker(threading.Thread):
    def __init__(self, pool: 'ThreadPool', worker_id: int):
        super().__init__(daemon=True)
        self.pool = pool
        self.worker_id = worker_id
        self.current_task: Optional[Task] = None
        self.tasks_completed = 0
    
    def run(self):
        while self.pool.running:
            try:
                task = self.pool.task_queue.get(timeout=1)
                if task is None:
                    break
                
                self.current_task = task
                task.status = TaskStatus.RUNNING
                
                try:
                    result = task.func(*task.args, **task.kwargs)
                    task.future.set_result(result)
                    task.status = TaskStatus.COMPLETED
                except Exception as e:
                    task.future.set_exception(e)
                    task.status = TaskStatus.FAILED
                
                self.tasks_completed += 1
                self.current_task = None
                self.pool.task_queue.task_done()
            except queue.Empty:
                continue

class ThreadPool:
    def __init__(self, num_workers: int = 4):
        self.num_workers = num_workers
        self.workers: List[Worker] = []
        self.task_queue = queue.Queue()
        self.running = False
        self.next_task_id = 1
        self.lock = threading.Lock()
    
    def start(self):
        self.running = True
        for i in range(self.num_workers):
            worker = Worker(self, i)
            worker.start()
            self.workers.append(worker)
    
    def stop(self, wait: bool = True):
        self.running = False
        
        if wait:
            self.task_queue.join()
        
        for _ in self.workers:
            self.task_queue.put(None)
        
        for worker in self.workers:
            worker.join(timeout=1)
        
        self.workers.clear()
    
    def submit(self, func: Callable, *args, **kwargs) -> Future:
        future = Future()
        
        with self.lock:
            task_id = self.next_task_id
            self.next_task_id += 1
        
        task = Task(
            id=task_id,
            func=func,
            args=args,
            kwargs=kwargs,
            future=future
        )
        
        self.task_queue.put(task)
        return future
    
    def map(self, func: Callable, items: List) -> List[Future]:
        futures = [self.submit(func, item) for item in items]
        return futures
    
    def get_stats(self) -> dict:
        active_workers = sum(1 for w in self.workers if w.current_task is not None)
        total_completed = sum(w.tasks_completed for w in self.workers)
        
        return {
            'workers': self.num_workers,
            'active': active_workers,
            'idle': self.num_workers - active_workers,
            'pending_tasks': self.task_queue.qsize(),
            'completed_tasks': total_completed
        }

class AsyncTask:
    def __init__(self, pool: ThreadPool):
        self.pool = pool
    
    def run(self, func: Callable, *args, **kwargs) -> Future:
        return self.pool.submit(func, *args, **kwargs)
    
    def run_all(self, funcs: List[Callable]) -> List[Future]:
        return [self.pool.submit(f) for f in funcs]
    
    def gather(self, futures: List[Future]) -> List[Any]:
        return [f.result() for f in futures]

def main():
    pool = ThreadPool(num_workers=4)
    pool.start()
    
    def compute(n: int) -> int:
        time.sleep(0.1)
        return n * n
    
    print("=== 提交任务 ===")
    futures = []
    for i in range(10):
        future = pool.submit(compute, i)
        futures.append(future)
    
    print(f"池状态: {pool.get_stats()}")
    
    print("\n=== 获取结果 ===")
    results = [f.result() for f in futures]
    print(f"结果: {results}")
    
    print("\n=== 使用map ===")
    items = list(range(5))
    map_futures = pool.map(compute, items)
    map_results = [f.result() for f in map_futures]
    print(f"map结果: {map_results}")
    
    print(f"\n最终状态: {pool.get_stats()}")
    
    pool.stop()


if __name__ == "__main__":
    main()
