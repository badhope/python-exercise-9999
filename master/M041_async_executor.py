# -----------------------------
# 题目：实现异步执行器。
# -----------------------------

import concurrent.futures
import threading
import queue
import time

class AsyncExecutor:
    def __init__(self, max_workers=4):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.futures = {}
        self.lock = threading.Lock()
    
    def submit(self, func, *args, **kwargs):
        future = self.executor.submit(func, *args, **kwargs)
        with self.lock:
            self.futures[future] = {"submitted_at": time.time()}
        return future
    
    def map(self, func, *iterables, timeout=None):
        return self.executor.map(func, *iterables, timeout=timeout)
    
    def wait(self, futures, timeout=None, return_when="ALL_COMPLETED"):
        return concurrent.futures.wait(futures, timeout=timeout, return_when=return_when)
    
    def shutdown(self, wait=True):
        self.executor.shutdown(wait=wait)
    
    def get_result(self, future, timeout=None):
        return future.result(timeout=timeout)

def slow_task(n):
    time.sleep(0.5)
    return f"Task {n} completed"

if __name__ == "__main__":
    executor = AsyncExecutor(max_workers=3)
    
    futures = [executor.submit(slow_task, i) for i in range(5)]
    
    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        print(result)
    
    executor.shutdown()
