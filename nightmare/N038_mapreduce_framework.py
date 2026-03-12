# -----------------------------
# 题目：实现分布式计算框架。
# 描述：支持MapReduce、任务分发、结果聚合。
# -----------------------------

import time
import threading
import random
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from queue import Queue
from collections import defaultdict

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class MapTask:
    task_id: str
    input_data: List[Any]
    mapper: Callable
    status: TaskStatus = TaskStatus.PENDING
    result: List[Tuple[Any, Any]] = field(default_factory=list)

@dataclass
class ReduceTask:
    task_id: str
    key: Any
    values: List[Any]
    reducer: Callable
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None

@dataclass
class Worker:
    worker_id: str
    status: str = "idle"
    current_task: Optional[str] = None
    completed_tasks: int = 0

class MapReduceJob:
    def __init__(self, job_id: str, mapper: Callable, reducer: Callable):
        self.job_id = job_id
        self.mapper = mapper
        self.reducer = reducer
        self.map_tasks: Dict[str, MapTask] = {}
        self.reduce_tasks: Dict[str, ReduceTask] = {}
        self.intermediate: Dict[Any, List[Any]] = defaultdict(list)
        self.result: Dict[Any, Any] = {}
        self.status = "initialized"
        self._task_counter = 0
        self._lock = threading.Lock()
    
    def add_input(self, data: List[Any]) -> str:
        with self._lock:
            self._task_counter += 1
            task_id = f"map-{self._task_counter}"
        
        task = MapTask(
            task_id=task_id,
            input_data=data,
            mapper=self.mapper
        )
        
        self.map_tasks[task_id] = task
        return task_id

class MapReduceMaster:
    def __init__(self, num_workers: int = 4):
        self.num_workers = num_workers
        self.workers: Dict[str, Worker] = {}
        self.jobs: Dict[str, MapReduceJob] = {}
        self._task_queue: Queue = Queue()
        self._result_queue: Queue = Queue()
        self._running = False
        self._worker_threads: List[threading.Thread] = []
        self._lock = threading.Lock()
        self._job_counter = 0
    
    def start(self):
        self._running = True
        
        for i in range(self.num_workers):
            worker_id = f"worker-{i}"
            self.workers[worker_id] = Worker(worker_id=worker_id)
            
            thread = threading.Thread(target=self._worker_loop, args=(worker_id,))
            thread.daemon = True
            thread.start()
            self._worker_threads.append(thread)
    
    def stop(self):
        self._running = False
        for thread in self._worker_threads:
            thread.join(timeout=1.0)
    
    def submit_job(self, mapper: Callable, reducer: Callable, input_data: List[List[Any]]) -> str:
        with self._lock:
            self._job_counter += 1
            job_id = f"job-{int(time.time())}-{self._job_counter}"
        
        job = MapReduceJob(job_id, mapper, reducer)
        
        for data in input_data:
            job.add_input(data)
        
        self.jobs[job_id] = job
        
        for task in job.map_tasks.values():
            self._task_queue.put(('map', job_id, task.task_id))
        
        return job_id
    
    def _worker_loop(self, worker_id: str):
        worker = self.workers[worker_id]
        
        while self._running:
            try:
                task_type, job_id, task_id = self._task_queue.get(timeout=0.5)
                
                worker.status = "busy"
                worker.current_task = task_id
                
                job = self.jobs.get(job_id)
                if not job:
                    continue
                
                if task_type == 'map':
                    self._execute_map_task(job, task_id)
                elif task_type == 'reduce':
                    self._execute_reduce_task(job, task_id)
                
                worker.completed_tasks += 1
                worker.status = "idle"
                worker.current_task = None
                
                self._check_job_progress(job_id)
            
            except:
                pass
    
    def _execute_map_task(self, job: MapReduceJob, task_id: str):
        task = job.map_tasks.get(task_id)
        if not task:
            return
        
        task.status = TaskStatus.RUNNING
        
        try:
            for item in task.input_data:
                result = task.mapper(item)
                if result:
                    for key, value in result:
                        task.result.append((key, value))
            
            task.status = TaskStatus.COMPLETED
            
            with job._lock:
                for key, value in task.result:
                    job.intermediate[key].append(value)
        
        except Exception as e:
            task.status = TaskStatus.FAILED
    
    def _execute_reduce_task(self, job: MapReduceJob, task_id: str):
        task = job.reduce_tasks.get(task_id)
        if not task:
            return
        
        task.status = TaskStatus.RUNNING
        
        try:
            task.result = task.reducer(task.key, task.values)
            task.status = TaskStatus.COMPLETED
            
            with job._lock:
                job.result[task.key] = task.result
        
        except Exception as e:
            task.status = TaskStatus.FAILED
    
    def _check_job_progress(self, job_id: str):
        job = self.jobs.get(job_id)
        if not job:
            return
        
        map_completed = all(
            t.status == TaskStatus.COMPLETED
            for t in job.map_tasks.values()
        )
        
        if map_completed and not job.reduce_tasks:
            self._create_reduce_tasks(job)
        
        reduce_completed = all(
            t.status == TaskStatus.COMPLETED
            for t in job.reduce_tasks.values()
        ) if job.reduce_tasks else False
        
        if map_completed and reduce_completed:
            job.status = "completed"
    
    def _create_reduce_tasks(self, job: MapReduceJob):
        with job._lock:
            for i, (key, values) in enumerate(job.intermediate.items()):
                task = ReduceTask(
                    task_id=f"reduce-{i}",
                    key=key,
                    values=values,
                    reducer=job.reducer
                )
                job.reduce_tasks[task.task_id] = task
                self._task_queue.put(('reduce', job.job_id, task.task_id))
    
    def get_job_result(self, job_id: str) -> Optional[Dict[Any, Any]]:
        job = self.jobs.get(job_id)
        if job and job.status == "completed":
            return job.result
        return None
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        job = self.jobs.get(job_id)
        if job:
            return {
                'job_id': job.job_id,
                'status': job.status,
                'map_tasks': len(job.map_tasks),
                'reduce_tasks': len(job.reduce_tasks),
                'map_completed': sum(1 for t in job.map_tasks.values() if t.status == TaskStatus.COMPLETED),
                'reduce_completed': sum(1 for t in job.reduce_tasks.values() if t.status == TaskStatus.COMPLETED)
            }
        return None

def main():
    master = MapReduceMaster(num_workers=3)
    master.start()
    
    def word_count_mapper(line: str) -> List[Tuple[str, int]]:
        words = line.lower().split()
        return [(word, 1) for word in words]
    
    def word_count_reducer(key: str, values: List[int]) -> int:
        return sum(values)
    
    print("提交词频统计任务...")
    input_data = [
        ["hello world hello python"],
        ["python is great hello"],
        ["world python programming"]
    ]
    
    job_id = master.submit_job(word_count_mapper, word_count_reducer, input_data)
    print(f"任务ID: {job_id}")
    
    time.sleep(2)
    
    print("\n任务状态:")
    status = master.get_job_status(job_id)
    print(f"  状态: {status['status']}")
    print(f"  Map任务: {status['map_completed']}/{status['map_tasks']}")
    print(f"  Reduce任务: {status['reduce_completed']}/{status['reduce_tasks']}")
    
    print("\n任务结果:")
    result = master.get_job_result(job_id)
    if result:
        for word, count in sorted(result.items(), key=lambda x: x[1], reverse=True):
            print(f"  {word}: {count}")
    
    master.stop()

if __name__ == "__main__":
    main()
