# -----------------------------
# 题目：实现分布式工作流引擎。
# 描述：支持流程定义、任务调度、状态管理。
# -----------------------------

import time
import threading
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from queue import Queue

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class WorkflowStatus(Enum):
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class TaskDefinition:
    task_id: str
    name: str
    handler: str
    dependencies: List[str] = field(default_factory=list)
    retry_count: int = 3
    timeout: float = 300.0
    params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TaskInstance:
    task_id: str
    definition: TaskDefinition
    status: TaskStatus = TaskStatus.PENDING
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Any = None
    error: Optional[str] = None
    retry_attempts: int = 0

@dataclass
class WorkflowDefinition:
    workflow_id: str
    name: str
    version: int = 1
    tasks: Dict[str, TaskDefinition] = field(default_factory=dict)
    
    def add_task(self, task: TaskDefinition):
        self.tasks[task.task_id] = task

@dataclass
class WorkflowInstance:
    instance_id: str
    workflow_id: str
    definition: WorkflowDefinition
    status: WorkflowStatus = WorkflowStatus.CREATED
    tasks: Dict[str, TaskInstance] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None

class TaskHandler:
    def __init__(self):
        self._handlers: Dict[str, Callable] = {}
    
    def register(self, name: str, handler: Callable):
        self._handlers[name] = handler
    
    def execute(self, name: str, params: Dict[str, Any], context: Dict[str, Any]) -> Any:
        handler = self._handlers.get(name)
        if handler:
            return handler(params, context)
        raise ValueError(f"Handler not found: {name}")

class WorkflowEngine:
    def __init__(self):
        self.definitions: Dict[str, WorkflowDefinition] = {}
        self.instances: Dict[str, WorkflowInstance] = {}
        self.handler = TaskHandler()
        self._task_queue: Queue = Queue()
        self._running = False
        self._worker_threads: List[threading.Thread] = []
        self._instance_counter = 0
        self._lock = threading.Lock()
    
    def register_handler(self, name: str, handler: Callable):
        self.handler.register(name, handler)
    
    def register_definition(self, definition: WorkflowDefinition):
        self.definitions[definition.workflow_id] = definition
    
    def start_workflow(self, workflow_id: str, context: Dict[str, Any] = None) -> str:
        definition = self.definitions.get(workflow_id)
        if not definition:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        with self._lock:
            self._instance_counter += 1
            instance_id = f"wf-{int(time.time())}-{self._instance_counter}"
        
        instance = WorkflowInstance(
            instance_id=instance_id,
            workflow_id=workflow_id,
            definition=definition,
            context=context or {}
        )
        
        for task_id, task_def in definition.tasks.items():
            instance.tasks[task_id] = TaskInstance(
                task_id=task_id,
                definition=task_def
            )
        
        self.instances[instance_id] = instance
        instance.status = WorkflowStatus.RUNNING
        instance.started_at = time.time()
        
        self._schedule_ready_tasks(instance)
        
        return instance_id
    
    def _schedule_ready_tasks(self, instance: WorkflowInstance):
        for task_id, task in instance.tasks.items():
            if task.status != TaskStatus.PENDING:
                continue
            
            dependencies_met = all(
                instance.tasks[dep_id].status == TaskStatus.COMPLETED
                for dep_id in task.definition.dependencies
                if dep_id in instance.tasks
            )
            
            if dependencies_met:
                self._task_queue.put((instance.instance_id, task_id))
    
    def start(self, num_workers: int = 4):
        self._running = True
        
        for i in range(num_workers):
            thread = threading.Thread(target=self._worker_loop)
            thread.daemon = True
            thread.start()
            self._worker_threads.append(thread)
    
    def stop(self):
        self._running = False
    
    def _worker_loop(self):
        while self._running:
            try:
                instance_id, task_id = self._task_queue.get(timeout=0.5)
                self._execute_task(instance_id, task_id)
            except:
                pass
    
    def _execute_task(self, instance_id: str, task_id: str):
        instance = self.instances.get(instance_id)
        if not instance:
            return
        
        task = instance.tasks.get(task_id)
        if not task:
            return
        
        task.status = TaskStatus.RUNNING
        task.started_at = time.time()
        
        try:
            result = self.handler.execute(
                task.definition.handler,
                task.definition.params,
                instance.context
            )
            
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = time.time()
            
            self._schedule_ready_tasks(instance)
            self._check_workflow_completion(instance)
        
        except Exception as e:
            task.retry_attempts += 1
            task.error = str(e)
            
            if task.retry_attempts >= task.definition.retry_count:
                task.status = TaskStatus.FAILED
                task.completed_at = time.time()
                instance.status = WorkflowStatus.FAILED
                instance.completed_at = time.time()
            else:
                task.status = TaskStatus.PENDING
                self._task_queue.put((instance_id, task_id))
    
    def _check_workflow_completion(self, instance: WorkflowInstance):
        all_completed = all(
            task.status == TaskStatus.COMPLETED
            for task in instance.tasks.values()
        )
        
        if all_completed:
            instance.status = WorkflowStatus.COMPLETED
            instance.completed_at = time.time()
    
    def get_workflow_status(self, instance_id: str) -> Optional[Dict[str, Any]]:
        instance = self.instances.get(instance_id)
        if not instance:
            return None
        
        return {
            'instance_id': instance.instance_id,
            'workflow_id': instance.workflow_id,
            'status': instance.status.value,
            'started_at': instance.started_at,
            'completed_at': instance.completed_at,
            'tasks': {
                task_id: {
                    'status': task.status.value,
                    'result': task.result,
                    'error': task.error
                }
                for task_id, task in instance.tasks.items()
            }
        }

def main():
    engine = WorkflowEngine()
    
    engine.register_handler("log", lambda p, c: print(f"  [LOG] {p.get('message', '')}"))
    engine.register_handler("compute", lambda p, c: p.get('a', 0) + p.get('b', 0))
    engine.register_handler("notify", lambda p, c: f"通知已发送: {p.get('to', '')}")
    
    definition = WorkflowDefinition(
        workflow_id="order-workflow",
        name="订单处理流程"
    )
    
    definition.add_task(TaskDefinition(
        task_id="validate",
        name="验证订单",
        handler="log",
        params={"message": "验证订单完成"}
    ))
    
    definition.add_task(TaskDefinition(
        task_id="calculate",
        name="计算金额",
        handler="compute",
        params={"a": 100, "b": 50},
        dependencies=["validate"]
    ))
    
    definition.add_task(TaskDefinition(
        task_id="notify_user",
        name="通知用户",
        handler="notify",
        params={"to": "user@example.com"},
        dependencies=["calculate"]
    ))
    
    engine.register_definition(definition)
    engine.start(num_workers=2)
    
    print("启动工作流...")
    instance_id = engine.start_workflow("order-workflow")
    print(f"实例ID: {instance_id}")
    
    time.sleep(2)
    
    print("\n工作流状态:")
    status = engine.get_workflow_status(instance_id)
    if status:
        print(f"  状态: {status['status']}")
        print("  任务:")
        for task_id, task in status['tasks'].items():
            print(f"    {task_id}: {task['status']}")
    
    engine.stop()

if __name__ == "__main__":
    main()
