# -----------------------------
# 题目：实现工作流引擎。
# -----------------------------

import time
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class WorkflowTask:
    def __init__(self, name, func, depends_on=None):
        self.name = name
        self.func = func
        self.depends_on = depends_on or []
        self.status = TaskStatus.PENDING
        self.result = None
        self.error = None
    
    def execute(self, context):
        self.status = TaskStatus.RUNNING
        try:
            self.result = self.func(context)
            self.status = TaskStatus.COMPLETED
            return True
        except Exception as e:
            self.error = e
            self.status = TaskStatus.FAILED
            return False

class Workflow:
    def __init__(self, name):
        self.name = name
        self.tasks = {}
        self.task_order = []
    
    def add_task(self, task):
        self.tasks[task.name] = task
    
    def build(self):
        self.task_order = []
        remaining = set(self.tasks.keys())
        
        while remaining:
            for task_name in list(remaining):
                task = self.tasks[task_name]
                if all(dep not in remaining for dep in task.depends_on):
                    self.task_order.append(task_name)
                    remaining.remove(task_name)
                    break
    
    def execute(self, context=None):
        if not self.task_order:
            self.build()
        
        context = context or {}
        results = {}
        
        for task_name in self.task_order:
            task = self.tasks[task_name]
            
            if not task.execute(context):
                print(f"Task {task_name} failed: {task.error}")
                return False
            
            results[task_name] = task.result
            context[task_name] = task.result
        
        return True

def task1(ctx):
    print("Task 1: Starting")
    time.sleep(0.1)
    return {"data": "from task 1"}

def task2(ctx):
    print("Task 2: Processing")
    time.sleep(0.1)
    return {"result": ctx.get("task1", {}).get("data", "") + " processed"}

def task3(ctx):
    print("Task 3: Finalizing")
    return {"final": "done"}

if __name__ == "__main__":
    wf = Workflow("example")
    wf.add_task(WorkflowTask("task1", task1))
    wf.add_task(WorkflowTask("task2", task2, depends_on=["task1"]))
    wf.add_task(WorkflowTask("task3", task3, depends_on=["task2"]))
    
    success = wf.execute()
    print(f"Workflow completed: {success}")
