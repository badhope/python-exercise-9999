# -----------------------------
# 题目：实现简单的任务队列。
# -----------------------------

import queue
import threading
import time
from dataclasses import dataclass
from typing import Callable, Any
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
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: str = None

class TaskQueue:
    def __init__(self, num_workers=4):
        self.queue = queue.Queue()
        self.workers = []
        self.num_workers = num_workers
        self.tasks = {}
        self.next_id = 1
        self.lock = threading.Lock()
        self.running = False
    
    def start(self):
        self.running = True
        for i in range(self.num_workers):
            worker = threading.Thread(target=self._worker, daemon=True)
            worker.start()
            self.workers.append(worker)
    
    def stop(self):
        self.running = False
        for _ in range(self.num_workers):
            self.queue.put(None)
        for worker in self.workers:
            worker.join(timeout=1)
        self.workers.clear()
    
    def submit(self, func, *args, **kwargs):
        with self.lock:
            task_id = self.next_id
            self.next_id += 1
        
        task = Task(id=task_id, func=func, args=args, kwargs=kwargs)
        self.tasks[task_id] = task
        self.queue.put(task)
        return task_id
    
    def get_task(self, task_id):
        return self.tasks.get(task_id)
    
    def get_status(self, task_id):
        task = self.tasks.get(task_id)
        return task.status if task else None
    
    def get_result(self, task_id):
        task = self.tasks.get(task_id)
        return task.result if task and task.status == TaskStatus.COMPLETED else None
    
    def _worker(self):
        while self.running:
            task = self.queue.get()
            if task is None:
                break
            
            task.status = TaskStatus.RUNNING
            try:
                task.result = task.func(*task.args, **task.kwargs)
                task.status = TaskStatus.COMPLETED
            except Exception as e:
                task.error = str(e)
                task.status = TaskStatus.FAILED
            
            self.queue.task_done()
    
    def wait_all(self, timeout=None):
        self.queue.join()

class TaskScheduler:
    def __init__(self):
        self.scheduled_tasks = []
        self.lock = threading.Lock()
    
    def schedule(self, func, delay=0, repeat=False, interval=0):
        task = {
            'func': func,
            'delay': delay,
            'repeat': repeat,
            'interval': interval,
            'next_run': time.time() + delay
        }
        with self.lock:
            self.scheduled_tasks.append(task)
        return task
    
    def run_pending(self):
        now = time.time()
        with self.lock:
            for task in self.scheduled_tasks[:]:
                if task['next_run'] <= now:
                    try:
                        task['func']()
                    except Exception as e:
                        print(f"任务执行失败: {e}")
                    
                    if task['repeat']:
                        task['next_run'] = now + task['interval']
                    else:
                        self.scheduled_tasks.remove(task)

def main():
    task_queue = TaskQueue(num_workers=2)
    task_queue.start()
    
    def process_data(data):
        time.sleep(0.5)
        return f"处理完成: {data}"
    
    print("=== 提交任务 ===")
    task_ids = []
    for i in range(5):
        task_id = task_queue.submit(process_data, f"数据{i}")
        task_ids.append(task_id)
        print(f"提交任务 {task_id}")
    
    print("\n=== 等待完成 ===")
    task_queue.wait_all()
    
    print("\n=== 获取结果 ===")
    for task_id in task_ids:
        result = task_queue.get_result(task_id)
        status = task_queue.get_status(task_id)
        print(f"任务 {task_id}: {status.value} - {result}")
    
    task_queue.stop()


if __name__ == "__main__":
    main()
