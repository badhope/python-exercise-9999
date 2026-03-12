# -----------------------------
# 题目：实现协程高级版。
# -----------------------------

import asyncio
from typing import Any, Callable, List, Dict, Coroutine
from dataclasses import dataclass
import time

@dataclass
class TaskResult:
    task_id: int
    result: Any
    error: Exception = None

class AsyncTaskManager:
    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self._results: Dict[int, TaskResult] = {}
        self._next_id = 0
    
    async def run(self, coro: Coroutine) -> TaskResult:
        task_id = self._next_id
        self._next_id += 1
        
        try:
            result = await coro
            task_result = TaskResult(task_id, result)
        except Exception as e:
            task_result = TaskResult(task_id, None, e)
        
        self._results[task_id] = task_result
        return task_result
    
    async def run_all(self, coros: List[Coroutine]) -> List[TaskResult]:
        tasks = [self.run(coro) for coro in coros]
        return await asyncio.gather(*tasks)
    
    async def run_with_limit(self, coros: List[Coroutine]) -> List[TaskResult]:
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def limited_run(coro):
            async with semaphore:
                return await self.run(coro)
        
        tasks = [limited_run(coro) for coro in coros]
        return await asyncio.gather(*tasks)

class AsyncQueue:
    def __init__(self, maxsize: int = 0):
        self._queue: asyncio.Queue = asyncio.Queue(maxsize)
    
    async def put(self, item: Any):
        await self._queue.put(item)
    
    async def get(self) -> Any:
        return await self._queue.get()
    
    async def put_nowait(self, item: Any):
        self._queue.put_nowait(item)
    
    def get_nowait(self) -> Any:
        return self._queue.get_nowait()
    
    def qsize(self) -> int:
        return self._queue.qsize()
    
    def empty(self) -> bool:
        return self._queue.empty()

class AsyncProducerConsumer:
    def __init__(self, queue_size: int = 10, num_consumers: int = 3):
        self.queue = AsyncQueue(queue_size)
        self.num_consumers = num_consumers
        self._running = False
    
    async def producer(self, items: List[Any]):
        for item in items:
            await self.queue.put(item)
            print(f"生产: {item}")
            await asyncio.sleep(0.01)
    
    async def consumer(self, consumer_id: int, processor: Callable):
        while self._running or not self.queue.empty():
            try:
                item = await asyncio.wait_for(self.queue.get(), timeout=0.1)
                result = await processor(item) if asyncio.iscoroutinefunction(processor) else processor(item)
                print(f"消费者{consumer_id}处理: {item} -> {result}")
            except asyncio.TimeoutError:
                continue
    
    async def run(self, items: List[Any], processor: Callable):
        self._running = True
        
        producers = [self.producer(items)]
        consumers = [self.consumer(i, processor) for i in range(self.num_consumers)]
        
        await asyncio.gather(*producers)
        self._running = False
        await asyncio.gather(*consumers)

class AsyncEventEmitter:
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}
    
    def on(self, event: str, listener: Callable):
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(listener)
    
    def off(self, event: str, listener: Callable):
        if event in self._listeners:
            self._listeners[event].remove(listener)
    
    async def emit(self, event: str, *args, **kwargs):
        if event in self._listeners:
            for listener in self._listeners[event]:
                if asyncio.iscoroutinefunction(listener):
                    await listener(*args, **kwargs)
                else:
                    listener(*args, **kwargs)

class AsyncCache:
    def __init__(self, ttl: int = 300):
        self._cache: Dict[str, Any] = {}
        self._timestamps: Dict[str, float] = {}
        self._ttl = ttl
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Any:
        async with self._lock:
            if key in self._cache:
                if time.time() - self._timestamps[key] < self._ttl:
                    return self._cache[key]
                else:
                    del self._cache[key]
                    del self._timestamps[key]
            return None
    
    async def set(self, key: str, value: Any):
        async with self._lock:
            self._cache[key] = value
            self._timestamps[key] = time.time()
    
    async def delete(self, key: str):
        async with self._lock:
            self._cache.pop(key, None)
            self._timestamps.pop(key, None)

async def async_retry(func: Callable, max_attempts: int = 3, delay: float = 1.0) -> Any:
    last_exception = None
    for attempt in range(max_attempts):
        try:
            if asyncio.iscoroutinefunction(func):
                return await func()
            return func()
        except Exception as e:
            last_exception = e
            if attempt < max_attempts - 1:
                await asyncio.sleep(delay)
    raise last_exception

async def async_timeout(coro: Coroutine, seconds: float) -> Any:
    return await asyncio.wait_for(coro, timeout=seconds)

async def main():
    print("=== AsyncTaskManager ===")
    manager = AsyncTaskManager(max_concurrent=2)
    
    async def compute(n):
        await asyncio.sleep(0.1)
        return n * n
    
    results = await manager.run_all([compute(i) for i in range(5)])
    for r in results:
        print(f"任务{r.task_id}: {r.result}")
    
    print("\n=== AsyncProducerConsumer ===")
    pc = AsyncProducerConsumer(queue_size=5, num_consumers=2)
    
    def process(x):
        return x * 2
    
    await pc.run(list(range(10)), process)
    
    print("\n=== AsyncEventEmitter ===")
    emitter = AsyncEventEmitter()
    
    async def on_message(msg):
        print(f"收到消息: {msg}")
    
    emitter.on('message', on_message)
    await emitter.emit('message', 'Hello Async!')
    
    print("\n=== AsyncCache ===")
    cache = AsyncCache(ttl=1)
    await cache.set('key1', 'value1')
    print(f"获取: {await cache.get('key1')}")
    
    await asyncio.sleep(1.1)
    print(f"过期后: {await cache.get('key1')}")


if __name__ == "__main__":
    asyncio.run(main())
