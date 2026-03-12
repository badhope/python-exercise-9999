# -----------------------------
# 题目：实现项目管理系统。
# 描述：管理项目、任务、进度、团队等。
# -----------------------------

from datetime import datetime, date
from enum import Enum

class TaskStatus(Enum):
    TODO = "待办"
    IN_PROGRESS = "进行中"
    DONE = "已完成"
    BLOCKED = "阻塞"

class Task:
    def __init__(self, task_id, title, assignee, due_date, priority="medium"):
        self.id = task_id
        self.title = title
        self.assignee = assignee
        self.due_date = due_date
        self.priority = priority
        self.status = TaskStatus.TODO
        self.created_at = datetime.now()
        self.completed_at = None
        self.subtasks = []
    
    def complete(self):
        self.status = TaskStatus.DONE
        self.completed_at = datetime.now()
    
    def is_overdue(self):
        return self.status != TaskStatus.DONE and date.today() > self.due_date

class Project:
    def __init__(self, project_id, name, start_date, end_date):
        self.id = project_id
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.tasks = []
        self.members = []
        self.status = "active"
    
    def get_progress(self):
        if not self.tasks:
            return 0
        completed = sum(1 for t in self.tasks if t.status == TaskStatus.DONE)
        return completed / len(self.tasks) * 100
    
    def is_overdue(self):
        return date.today() > self.end_date and self.status == "active"

class ProjectSystem:
    def __init__(self):
        self.projects = {}
        self.tasks = {}
        self.next_project_id = 1
        self.next_task_id = 1
    
    def create_project(self, name, start_date, end_date):
        project = Project(self.next_project_id, name, start_date, end_date)
        self.projects[self.next_project_id] = project
        self.next_project_id += 1
        return project.id
    
    def add_task(self, project_id, title, assignee, due_date, priority="medium"):
        project = self.projects.get(project_id)
        if project:
            task = Task(self.next_task_id, title, assignee, due_date, priority)
            self.tasks[self.next_task_id] = task
            project.tasks.append(task)
            self.next_task_id += 1
            return task.id
        return None
    
    def update_task_status(self, task_id, status):
        task = self.tasks.get(task_id)
        if task:
            task.status = status
            if status == TaskStatus.DONE:
                task.completed_at = datetime.now()
            return True
        return False
    
    def add_project_member(self, project_id, member_name):
        project = self.projects.get(project_id)
        if project and member_name not in project.members:
            project.members.append(member_name)
            return True
        return False
    
    def get_project_tasks(self, project_id, status=None):
        project = self.projects.get(project_id)
        if project:
            if status:
                return [t for t in project.tasks if t.status == status]
            return project.tasks
        return []
    
    def get_overdue_tasks(self):
        return [t for t in self.tasks.values() if t.is_overdue()]
    
    def get_member_tasks(self, member_name, status=None):
        tasks = [t for t in self.tasks.values() if t.assignee == member_name]
        if status:
            tasks = [t for t in tasks if t.status == status]
        return tasks
    
    def get_project_summary(self, project_id):
        project = self.projects.get(project_id)
        if project:
            total = len(project.tasks)
            completed = sum(1 for t in project.tasks if t.status == TaskStatus.DONE)
            in_progress = sum(1 for t in project.tasks if t.status == TaskStatus.IN_PROGRESS)
            
            return {
                'name': project.name,
                'progress': project.get_progress(),
                'total_tasks': total,
                'completed': completed,
                'in_progress': in_progress,
                'overdue': sum(1 for t in project.tasks if t.is_overdue()),
                'members': project.members
            }
        return None
    
    def get_stats(self):
        return {
            'projects': len(self.projects),
            'active_projects': sum(1 for p in self.projects.values() if p.status == "active"),
            'total_tasks': len(self.tasks),
            'completed_tasks': sum(1 for t in self.tasks.values() if t.status == TaskStatus.DONE),
            'overdue_tasks': len(self.get_overdue_tasks())
        }

def main():
    system = ProjectSystem()
    
    p1 = system.create_project("网站重构", date(2024, 1, 1), date(2024, 3, 31))
    p2 = system.create_project("APP开发", date(2024, 2, 1), date(2024, 6, 30))
    
    system.add_project_member(p1, "张三")
    system.add_project_member(p1, "李四")
    system.add_project_member(p2, "王五")
    
    t1 = system.add_task(p1, "需求分析", "张三", date(2024, 1, 15), "high")
    t2 = system.add_task(p1, "UI设计", "李四", date(2024, 1, 31), "medium")
    t3 = system.add_task(p1, "前端开发", "张三", date(2024, 2, 28), "high")
    
    system.update_task_status(t1, TaskStatus.DONE)
    system.update_task_status(t2, TaskStatus.IN_PROGRESS)
    
    print("项目系统统计:")
    stats = system.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print(f"\n项目'{system.projects[p1].name}'概要:")
    summary = system.get_project_summary(p1)
    for key, value in summary.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
