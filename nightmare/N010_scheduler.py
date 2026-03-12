# -----------------------------
# 题目：实现简单的分布式调度器。
# 描述：支持任务调度、故障转移、负载均衡。
# -----------------------------

import time
import threading
import heapq
from enum import Enum
from collections import defaultdict

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class Task:
    def __init__(self, task_id, func, args=None, kwargs=None, priority=0):
        self.task_id = task_id
        self.func = func
        self.args = args or ()
        self.kwargs = kwargs or {}
        self.priority = priority
        self.status = TaskStatus.PENDING
        self.assigned_worker = None
        self.retries = 0
        self.max_retries = 3
        self.created_at = time.time()
    
    def __lt__(self, other):
        return self.priority > other.priority

class Worker:
    def __init__(self, worker_id):
        self.worker_id = worker_id
        self.status = "idle"
        self.current_task = None
        self.completed_tasks = 0
        self.failed_tasks = 0
        self.last_heartbeat = time.time()
    
    def is_available(self):
        return self.status == "idle" and time.time() - self.last_heartbeat < 30

class Scheduler:
    def __init__(self):
        self.task_queue = []
        self.workers = {}
        self.tasks = {}
        self._lock = threading.Lock()
    
    def register_worker(self, worker_id):
        with self._lock:
            self.workers[worker_id] = Worker(worker_id)
    
    def unregister_worker(self, worker_id):
        with self._lock:
            self.workers.pop(worker_id, None)
    
    def submit(self, task):
        with self._lock:
            self.tasks[task.task_id] = task
            heapq.heappush(self.task_queue, task)
    
    def assign_task(self):
        with self._lock:
            if not self.task_queue:
                return None
            
            available_workers = [w for w in self.workers.values() if w.is_available()]
            if not available_workers:
                return None
            
            worker = min(available_workers, key=lambda w: w.completed_tasks)
            task = heapq.heappop(self.task_queue)
            
            task.status = TaskStatus.RUNNING
            task.assigned_worker = worker.worker_id
            worker.status = "busy"
            worker.current_task = task
            
            return task, worker
    
    def complete_task(self, task_id, success=True):
        with self._lock:
            task = self.tasks.get(task_id)
            if not task:
                return
            
            worker = self.workers.get(task.assigned_worker)
            if worker:
                worker.status = "idle"
                worker.current_task = None
                if success:
                    worker.completed_tasks += 1
                    task.status = TaskStatus.COMPLETED
                else:
                    worker.failed_tasks += 1
                    if task.retries < task.max_retries:
                        task.retries += 1
                        task.status = TaskStatus.PENDING
                        heapq.heappush(self.task_queue, task)
                    else:
                        task.status = TaskStatus.FAILED
    
    def get_stats(self):
        with self._lock:
            return {
                'total_tasks': len(self.tasks),
                'pending': len(self.task_queue),
                'workers': len(self.workers),
                'available_workers': sum(1 for w in self.workers.values() if w.is_available())
            }

class WorkerNode(threading.Thread):
    def __init__(self, worker_id, scheduler):
        super().__init__()
        self.worker_id = worker_id
        self.scheduler = scheduler
        self.running = True
        self.daemon = True
    
    def run(self):
        self.scheduler.register_worker(self.worker_id)
        
        while self.running:
            result = self.scheduler.assign_task()
            if result:
                task, worker = result
                try:
                    task.func(*task.args, **task.kwargs)
                    self.scheduler.complete_task(task.task_id, True)
                except Exception:
                    self.scheduler.complete_task(task.task_id, False)
            else:
                time.sleep(0.1)

def main():
    scheduler = Scheduler()
    
    workers = [WorkerNode(f"worker-{i}", scheduler) for i in range(3)]
    for w in workers:
        w.start()
    
    def sample_task(n):
        time.sleep(0.1)
        return n * 2
    
    for i in range(5):
        task = Task(f"task-{i}", sample_task, (i,), priority=i)
        scheduler.submit(task)
    
    time.sleep(2)
    print(f"调度器状态: {scheduler.get_stats()}")


if __name__ == "__main__":
    main()
