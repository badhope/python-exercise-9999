# -----------------------------
# 题目：实现任务调度器。
# -----------------------------

import time
import threading
from datetime import datetime, timedelta
from collections import defaultdict

class Task:
    def __init__(self, name, func, interval=None, at_time=None):
        self.name = name
        self.func = func
        self.interval = interval
        self.at_time = at_time
        self.last_run = None
        self.next_run = None
    
    def should_run(self):
        now = datetime.now()
        if self.next_run is None:
            if self.at_time:
                hour, minute = map(int, self.at_time.split(':'))
                self.next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                if self.next_run <= now:
                    self.next_run += timedelta(days=1)
            elif self.interval:
                self.next_run = now
            return True
        return now >= self.next_run
    
    def run(self):
        try:
            self.func()
            self.last_run = datetime.now()
            if self.interval:
                self.next_run = self.last_run + timedelta(seconds=self.interval)
            elif self.at_time:
                self.next_run += timedelta(days=1)
        except Exception as e:
            print(f"Task {self.name} failed: {e}")

class TaskScheduler:
    def __init__(self):
        self.tasks = {}
        self.running = False
        self.thread = None
        self.lock = threading.Lock()
    
    def add_task(self, task):
        with self.lock:
            self.tasks[task.name] = task
    
    def remove_task(self, name):
        with self.lock:
            self.tasks.pop(name, None)
    
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
    
    def _run_loop(self):
        while self.running:
            with self.lock:
                tasks_to_run = [t for t in self.tasks.values() if t.should_run()]
            
            for task in tasks_to_run:
                threading.Thread(target=task.run, daemon=True).start()
            
            time.sleep(1)

def my_task():
    print(f"Task executed at {datetime.now()}")

if __name__ == "__main__":
    scheduler = TaskScheduler()
    task = Task("print_time", my_task, interval=5)
    scheduler.add_task(task)
    scheduler.start()
    
    print("Scheduler running for 15 seconds...")
    time.sleep(15)
    scheduler.stop()
    print("Scheduler stopped")
