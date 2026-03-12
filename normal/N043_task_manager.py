# -----------------------------
# 题目：实现简单的待办事项管理器。
# 描述：管理待办事项，支持优先级和状态。
# -----------------------------

from datetime import datetime, date

class Task:
    def __init__(self, task_id, title, priority="medium", due_date=None):
        self.id = task_id
        self.title = title
        self.priority = priority
        self.due_date = due_date
        self.status = "pending"
        self.created_at = datetime.now()
        self.completed_at = None
    
    def complete(self):
        self.status = "completed"
        self.completed_at = datetime.now()
    
    def reopen(self):
        self.status = "pending"
        self.completed_at = None
    
    def is_overdue(self):
        if self.due_date and self.status == "pending":
            return date.today() > self.due_date
        return False
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'priority': self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class TaskManager:
    def __init__(self):
        self.tasks = {}
        self.next_id = 1
        self.priority_order = {"high": 0, "medium": 1, "low": 2}
    
    def add(self, title, priority="medium", due_date=None):
        task = Task(self.next_id, title, priority, due_date)
        self.tasks[self.next_id] = task
        self.next_id += 1
        return task.id
    
    def get(self, task_id):
        return self.tasks.get(task_id)
    
    def delete(self, task_id):
        if task_id in self.tasks:
            del self.tasks[task_id]
            return True
        return False
    
    def complete(self, task_id):
        task = self.tasks.get(task_id)
        if task:
            task.complete()
            return True
        return False
    
    def reopen(self, task_id):
        task = self.tasks.get(task_id)
        if task:
            task.reopen()
            return True
        return False
    
    def get_pending(self):
        return [t for t in self.tasks.values() if t.status == "pending"]
    
    def get_completed(self):
        return [t for t in self.tasks.values() if t.status == "completed"]
    
    def get_overdue(self):
        return [t for t in self.tasks.values() if t.is_overdue()]
    
    def get_by_priority(self, priority):
        return [t for t in self.tasks.values() if t.priority == priority]
    
    def sort_by_priority(self):
        return sorted(
            self.tasks.values(),
            key=lambda t: (self.priority_order.get(t.priority, 1), t.created_at)
        )
    
    def get_stats(self):
        total = len(self.tasks)
        completed = len(self.get_completed())
        pending = len(self.get_pending())
        overdue = len(self.get_overdue())
        
        return {
            'total': total,
            'completed': completed,
            'pending': pending,
            'overdue': overdue,
            'completion_rate': f"{completed/total*100:.1f}%" if total > 0 else "0%"
        }

def main():
    manager = TaskManager()
    
    manager.add("学习Python", "high")
    manager.add("写项目文档", "medium")
    manager.add("代码审查", "low")
    
    manager.complete(1)
    
    print("待办事项统计:")
    stats = manager.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n按优先级排序:")
    for task in manager.sort_by_priority():
        status = "✓" if task.status == "completed" else "○"
        print(f"  {status} [{task.priority}] {task.title}")


if __name__ == "__main__":
    main()
