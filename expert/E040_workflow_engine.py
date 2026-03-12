# -----------------------------
# 题目：实现工作流引擎。
# -----------------------------

from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class TaskResult:
    status: TaskStatus
    output: Any = None
    error: str = None

@dataclass
class Task:
    id: str
    name: str
    action: Callable
    dependencies: List[str] = field(default_factory=list)
    condition: Callable = None
    retry_count: int = 0
    timeout: int = None
    status: TaskStatus = TaskStatus.PENDING
    result: TaskResult = None

@dataclass
class WorkflowContext:
    id: str
    variables: Dict[str, Any] = field(default_factory=dict)
    task_results: Dict[str, TaskResult] = field(default_factory=dict)
    start_time: datetime = None
    end_time: datetime = None

class Workflow:
    def __init__(self, name: str):
        self.name = name
        self.tasks: Dict[str, Task] = {}
        self.variables: Dict[str, Any] = {}
    
    def add_task(self, name: str, action: Callable, 
                 dependencies: List[str] = None, 
                 condition: Callable = None) -> 'Workflow':
        task_id = str(uuid.uuid4())[:8]
        task = Task(
            id=task_id,
            name=name,
            action=action,
            dependencies=dependencies or [],
            condition=condition
        )
        self.tasks[task_id] = task
        return self
    
    def set_variable(self, key: str, value: Any) -> 'Workflow':
        self.variables[key] = value
        return self
    
    def get_entry_tasks(self) -> List[Task]:
        return [t for t in self.tasks.values() if not t.dependencies]
    
    def get_dependent_tasks(self, task_id: str) -> List[Task]:
        return [t for t in self.tasks.values() if task_id in t.dependencies]

class WorkflowEngine:
    def __init__(self):
        self._workflows: Dict[str, Workflow] = {}
    
    def register(self, workflow: Workflow):
        self._workflows[workflow.name] = workflow
    
    def execute(self, workflow_name: str, variables: Dict[str, Any] = None) -> WorkflowContext:
        workflow = self._workflows.get(workflow_name)
        if not workflow:
            raise ValueError(f"工作流 {workflow_name} 未注册")
        
        context = WorkflowContext(
            id=str(uuid.uuid4())[:8],
            variables={**workflow.variables, **(variables or {})},
            start_time=datetime.now()
        )
        
        completed_tasks: set = set()
        
        while len(completed_tasks) < len(workflow.tasks):
            ready_tasks = self._get_ready_tasks(workflow, completed_tasks, context)
            
            if not ready_tasks:
                break
            
            for task in ready_tasks:
                self._execute_task(task, context)
                completed_tasks.add(task.id)
        
        context.end_time = datetime.now()
        return context
    
    def _get_ready_tasks(self, workflow: Workflow, completed: set, 
                         context: WorkflowContext) -> List[Task]:
        ready = []
        
        for task in workflow.tasks.values():
            if task.id in completed:
                continue
            
            if task.status != TaskStatus.PENDING:
                continue
            
            deps_completed = all(
                dep_id in completed for dep_id in task.dependencies
            )
            
            if not deps_completed:
                continue
            
            if task.condition:
                if not task.condition(context):
                    task.status = TaskStatus.SKIPPED
                    task.result = TaskResult(status=TaskStatus.SKIPPED)
                    context.task_results[task.id] = task.result
                    completed.add(task.id)
                    continue
            
            ready.append(task)
        
        return ready
    
    def _execute_task(self, task: Task, context: WorkflowContext):
        task.status = TaskStatus.RUNNING
        
        try:
            result = task.action(context)
            task.status = TaskStatus.COMPLETED
            task.result = TaskResult(status=TaskStatus.COMPLETED, output=result)
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.result = TaskResult(status=TaskStatus.FAILED, error=str(e))
        
        context.task_results[task.id] = task.result

class WorkflowBuilder:
    def __init__(self, name: str):
        self.workflow = Workflow(name)
    
    def task(self, name: str, action: Callable) -> 'WorkflowBuilder':
        self.workflow.add_task(name, action)
        return self
    
    def task_with_deps(self, name: str, action: Callable, 
                       deps: List[str]) -> 'WorkflowBuilder':
        dep_ids = [self._get_task_id(d) for d in deps if self._get_task_id(d)]
        self.workflow.add_task(name, action, dependencies=dep_ids)
        return self
    
    def _get_task_id(self, name: str) -> Optional[str]:
        for task in self.workflow.tasks.values():
            if task.name == name:
                return task.id
        return None
    
    def variable(self, key: str, value: Any) -> 'WorkflowBuilder':
        self.workflow.set_variable(key, value)
        return self
    
    def build(self) -> Workflow:
        return self.workflow

def main():
    print("=== 构建工作流 ===")
    
    def fetch_data(ctx: WorkflowContext):
        print("  获取数据...")
        return {"users": ["张三", "李四"]}
    
    def process_data(ctx: WorkflowContext):
        print("  处理数据...")
        data = ctx.task_results.get(list(ctx.task_results.keys())[0])
        if data and data.output:
            return [u.upper() for u in data.output.get("users", [])]
        return []
    
    def save_data(ctx: WorkflowContext):
        print("  保存数据...")
        return "保存成功"
    
    def notify(ctx: WorkflowContext):
        print("  发送通知...")
        return "通知已发送"
    
    workflow = (WorkflowBuilder("数据处理流程")
                .task("fetch", fetch_data)
                .task_with_deps("process", process_data, ["fetch"])
                .task_with_deps("save", save_data, ["process"])
                .task_with_deps("notify", notify, ["save"])
                .variable("debug", True)
                .build())
    
    engine = WorkflowEngine()
    engine.register(workflow)
    
    print("\n=== 执行工作流 ===")
    context = engine.execute("数据处理流程")
    
    print(f"\n=== 执行结果 ===")
    print(f"工作流ID: {context.id}")
    print(f"开始时间: {context.start_time}")
    print(f"结束时间: {context.end_time}")
    
    print("\n任务结果:")
    for task_id, result in context.task_results.items():
        print(f"  {task_id}: {result.status.value} - {result.output or result.error}")


if __name__ == "__main__":
    main()
