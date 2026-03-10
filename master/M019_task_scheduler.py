# -----------------------------
# 题目：实现简单的任务调度器。
# -----------------------------

import time
import threading
from datetime import datetime
from collections import deque

class Task:
    def __init__(self, task_id, func, args=(), delay=0):
        self.task_id = task_id
        self.func = func
        self.args = args
        self.delay = delay
        self.execute_time = time.time() + delay

class TaskScheduler:
    def __init__(self):
        self.tasks = []
        self.running = False
        self.lock = threading.Lock()
    
    def add_task(self, task):
        with self.lock:
            self.tasks.append(task)
            self.tasks.sort(key=lambda t: t.execute_time)
    
    def run(self):
        self.running = True
        while self.running:
            with self.lock:
                if not self.tasks:
                    time.sleep(0.1)
                    continue
                now = time.time()
                if self.tasks[0].execute_time <= now:
                    task = self.tasks.pop(0)
                    try:
                        task.func(*task.args)
                    except Exception as e:
                        print(f"任务执行错误: {e}")
            time.sleep(0.1)
    
    def stop(self):
        self.running = False

def my_task(name):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 执行任务: {name}")

def main():
    scheduler = TaskScheduler()
    scheduler.add_task(Task(1, my_task, ("任务A",), delay=1))
    scheduler.add_task(Task(2, my_task, ("任务B",), delay=2))
    scheduler.add_task(Task(3, my_task, ("任务C",), delay=0.5))
    thread = threading.Thread(target=scheduler.run)
    thread.start()
    time.sleep(3)
    scheduler.stop()
    thread.join()


if __name__ == "__main__":
    main()
