# -----------------------------
# 题目：实现简单的分布式任务队列。
# 描述：支持任务分发、执行、重试。
# -----------------------------

import queue
import threading
import time
import uuid
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class Task:
    def __init__(self, task_id, func, args=None, kwargs=None, max_retries=3):
        self.task_id = task_id
        self.func = func
        self.args = args or ()
        self.kwargs = kwargs or {}
        self.max_retries = max_retries
        self.retries = 0
        self.status = TaskStatus.PENDING
        self.result = None
        self.error = None

class Worker(threading.Thread):
    def __init__(self, worker_id, task_queue, result_queue):
        super().__init__()
        self.worker_id = worker_id
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.running = True
        self.daemon = True
    
    def run(self):
        while self.running:
            try:
                task = self.task_queue.get(timeout=1)
                self.execute_task(task)
            except queue.Empty:
                continue
    
    def execute_task(self, task):
        task.status = TaskStatus.RUNNING
        try:
            task.result = task.func(*task.args, **task.kwargs)
            task.status = TaskStatus.COMPLETED
        except Exception as e:
            task.error = str(e)
            if task.retries < task.max_retries:
                task.retries += 1
                task.status = TaskStatus.PENDING
                self.task_queue.put(task)
                return
            task.status = TaskStatus.FAILED
        
        self.result_queue.put(task)
    
    def stop(self):
        self.running = False

class TaskQueue:
    def __init__(self, num_workers=4):
        self.task_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.workers = []
        self.tasks = {}
        
        for i in range(num_workers):
            worker = Worker(i, self.task_queue, self.result_queue)
            worker.start()
            self.workers.append(worker)
    
    def submit(self, func, *args, max_retries=3, **kwargs):
        task_id = str(uuid.uuid4())
        task = Task(task_id, func, args, kwargs, max_retries)
        self.tasks[task_id] = task
        self.task_queue.put(task)
        return task_id
    
    def get_result(self, task_id, timeout=None):
        task = self.tasks.get(task_id)
        if task and task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            return task
        return None
    
    def shutdown(self):
        for worker in self.workers:
            worker.stop()
        for worker in self.workers:
            worker.join()

def main():
    tq = TaskQueue(2)
    
    def slow_task(n):
        time.sleep(0.1)
        return n ** 2
    
    task_ids = [tq.submit(slow_task, i) for i in range(5)]
    
    time.sleep(1)
    
    for task_id in task_ids:
        task = tq.get_result(task_id)
        if task:
            print(f"任务 {task_id[:8]}: {task.status.value}, 结果: {task.result}")
    
    tq.shutdown()


if __name__ == "__main__":
    main()
