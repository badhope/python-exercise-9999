# -----------------------------
# 题目：实现分布式锁。
# -----------------------------

import time
import threading
import uuid
from contextlib import contextmanager

class LockAcquireError(Exception):
    pass

class DistributedLock:
    def __init__(self, name, ttl=30):
        self.name = name
        self.ttl = ttl
        self._lock = threading.Lock()
        self._ holders = {}
    
    def acquire(self, holder_id=None, timeout=None):
        if holder_id is None:
            holder_id = str(uuid.uuid4())
        
        start_time = time.time()
        while True:
            with self._lock:
                if holder_id not in self._holders:
                    self._holders[holder_id] = time.time() + self.ttl
                    return holder_id
            
            if timeout is not None and time.time() - start_time >= timeout:
                raise LockAcquireError(f"Failed to acquire lock: {self.name}")
            
            time.sleep(0.1)
    
    def release(self, holder_id):
        with self._lock:
            if holder_id in self._holders:
                del self._holders[holder_id]
                return True
            return False
    
    @contextmanager
    def lock(self, holder_id=None, timeout=None):
        holder_id = self.acquire(holder_id, timeout)
        try:
            yield holder_id
        finally:
            self.release(holder_id)
    
    def is_locked(self):
        with self._lock:
            current_time = time.time()
            expired = [h for h, exp in self._holders.items() if exp < current_time]
            for h in expired:
                del self._holders[h]
            return len(self._holders) > 0

if __name__ == "__main__":
    lock = DistributedLock("test_lock")
    
    def worker(worker_id):
        print(f"Worker {worker_id} trying to acquire lock...")
        with lock.lock(timeout=5) as holder_id:
            print(f"Worker {worker_id} acquired lock")
            time.sleep(2)
            print(f"Worker {worker_id} releasing lock")
    
    threads = [threading.Thread(target=worker, args=(i,)) for i in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print("All workers completed")
