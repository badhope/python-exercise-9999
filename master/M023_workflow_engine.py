# -----------------------------
# 题目：实现工作流引擎。
# 描述：支持流程定义、执行、状态管理。
# -----------------------------

import time
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

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
    error: Optional[str] = None

class WorkflowTask(ABC):
    def __init__(self, task_id: str, name: str):
        self.task_id = task_id
        self.name = name
        self.dependencies: List[str] = []
        self.status = TaskStatus.PENDING
        self.result: Optional[TaskResult] = None
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> TaskResult:
        pass
    
    def add_dependency(self, task_id: str):
        self.dependencies.append(task_id)

class FunctionTask(WorkflowTask):
    def __init__(self, task_id: str, name: str, func: Callable, **kwargs):
        super().__init__(task_id, name)
        self.func = func
        self.kwargs = kwargs
    
    def execute(self, context: Dict[str, Any]) -> TaskResult:
        try:
            merged_kwargs = {**context, **self.kwargs}
            result = self.func(**merged_kwargs)
            return TaskResult(status=TaskStatus.COMPLETED, output=result)
        except Exception as e:
            return TaskResult(status=TaskStatus.FAILED, error=str(e))

class ConditionalTask(WorkflowTask):
    def __init__(
        self,
        task_id: str,
        name: str,
        condition: Callable[[Dict], bool],
        true_task: WorkflowTask,
        false_task: WorkflowTask = None
    ):
        super().__init__(task_id, name)
        self.condition = condition
        self.true_task = true_task
        self.false_task = false_task
    
    def execute(self, context: Dict[str, Any]) -> TaskResult:
        try:
            if self.condition(context):
                result = self.true_task.execute(context)
            elif self.false_task:
                result = self.false_task.execute(context)
            else:
                result = TaskResult(status=TaskStatus.SKIPPED)
            return result
        except Exception as e:
            return TaskResult(status=TaskStatus.FAILED, error=str(e))

class ParallelTask(WorkflowTask):
    def __init__(self, task_id: str, name: str, tasks: List[WorkflowTask]):
        super().__init__(task_id, name)
        self.tasks = tasks
    
    def execute(self, context: Dict[str, Any]) -> TaskResult:
        import threading
        results = {}
        errors = []
        
        def run_task(task: WorkflowTask):
            try:
                result = task.execute(context)
                results[task.task_id] = result
            except Exception as e:
                errors.append(str(e))
        
        threads = []
        for task in self.tasks:
            t = threading.Thread(target=run_task, args=(task,))
            t.start()
            threads.append(t)
        
        for t in threads:
            t.join()
        
        if errors:
            return TaskResult(status=TaskStatus.FAILED, error="; ".join(errors))
        return TaskResult(status=TaskStatus.COMPLETED, output=results)

@dataclass
class WorkflowDefinition:
    workflow_id: str
    name: str
    tasks: Dict[str, WorkflowTask] = field(default_factory=dict)
    initial_context: Dict[str, Any] = field(default_factory=dict)
    
    def add_task(self, task: WorkflowTask):
        self.tasks[task.task_id] = task
        return self

@dataclass
class WorkflowInstance:
    instance_id: str
    workflow_id: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    context: Dict[str, Any] = field(default_factory=dict)
    task_results: Dict[str, TaskResult] = field(default_factory=dict)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None

class WorkflowEngine:
    def __init__(self):
        self.definitions: Dict[str, WorkflowDefinition] = {}
        self.instances: Dict[str, WorkflowInstance] = {}
        self._instance_counter = 0
    
    def register(self, definition: WorkflowDefinition):
        self.definitions[definition.workflow_id] = definition
    
    def start(self, workflow_id: str, context: Dict[str, Any] = None) -> str:
        definition = self.definitions.get(workflow_id)
        if not definition:
            raise ValueError(f"工作流未注册: {workflow_id}")
        
        self._instance_counter += 1
        instance_id = f"inst-{int(time.time())}-{self._instance_counter}"
        
        instance = WorkflowInstance(
            instance_id=instance_id,
            workflow_id=workflow_id,
            context={**definition.initial_context, **(context or {})}
        )
        
        self.instances[instance_id] = instance
        self._execute_workflow(instance, definition)
        
        return instance_id
    
    def _execute_workflow(self, instance: WorkflowInstance, definition: WorkflowDefinition):
        instance.status = WorkflowStatus.RUNNING
        instance.started_at = time.time()
        
        executed = set()
        
        while len(executed) < len(definition.tasks):
            progress = False
            
            for task_id, task in definition.tasks.items():
                if task_id in executed:
                    continue
                
                if self._can_execute(task, executed, instance):
                    task.status = TaskStatus.RUNNING
                    result = task.execute(instance.context)
                    task.result = result
                    instance.task_results[task_id] = result
                    
                    if result.status == TaskStatus.COMPLETED:
                        if result.output:
                            instance.context[f"task_{task_id}"] = result.output
                        executed.add(task_id)
                        progress = True
                    elif result.status == TaskStatus.FAILED:
                        instance.status = WorkflowStatus.FAILED
                        instance.completed_at = time.time()
                        return
            
            if not progress:
                break
        
        instance.status = WorkflowStatus.COMPLETED
        instance.completed_at = time.time()
    
    def _can_execute(
        self,
        task: WorkflowTask,
        executed: set,
        instance: WorkflowInstance
    ) -> bool:
        for dep_id in task.dependencies:
            if dep_id not in executed:
                return False
            if instance.task_results.get(dep_id, TaskResult(TaskStatus.PENDING)).status != TaskStatus.COMPLETED:
                return False
        return True
    
    def get_instance(self, instance_id: str) -> Optional[WorkflowInstance]:
        return self.instances.get(instance_id)
    
    def get_status(self, instance_id: str) -> Optional[WorkflowStatus]:
        instance = self.instances.get(instance_id)
        return instance.status if instance else None

def main():
    engine = WorkflowEngine()
    
    def step1(**kwargs):
        print("执行步骤1: 数据准备")
        return {"data": "prepared"}
    
    def step2(**kwargs):
        print("执行步骤2: 数据处理")
        data = kwargs.get("task_step1", {}).get("data", "")
        return {"processed": data.upper()}
    
    def step3(**kwargs):
        print("执行步骤3: 数据保存")
        return {"saved": True}
    
    workflow = WorkflowDefinition("wf-001", "数据处理流程")
    workflow.add_task(FunctionTask("step1", "数据准备", step1))
    workflow.add_task(FunctionTask("step2", "数据处理", step2))
    workflow.add_task(FunctionTask("step3", "数据保存", step3))
    
    workflow.tasks["step2"].add_dependency("step1")
    workflow.tasks["step3"].add_dependency("step2")
    
    engine.register(workflow)
    
    instance_id = engine.start("wf-001", {"user": "张三"})
    
    instance = engine.get_instance(instance_id)
    print(f"\n工作流状态: {instance.status.value}")
    print(f"执行结果: {instance.task_results}")

if __name__ == "__main__":
    main()
