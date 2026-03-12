# -----------------------------
# 题目：实现简单的分布式锁。
# 描述：支持锁获取、释放、续期。
# -----------------------------

import time
import threading
import uuid

class DistributedLock:
    def __init__(self, lock_name, ttl=30):
        self.lock_name = lock_name
        self.ttl = ttl
        self.lock_id = str(uuid.uuid4())
        self.acquired = False
        self._lock = threading.Lock()
    
    def acquire(self, timeout=10):
        start_time = time.time()
        while time.time() - start_time < timeout:
            with self._lock:
                if not self.acquired:
                    self.acquired = True
                    self._expire_time = time.time() + self.ttl
                    return True
            time.sleep(0.01)
        return False
    
    def release(self):
        with self._lock:
            if self.acquired:
                self.acquired = False
                return True
        return False
    
    def renew(self):
        with self._lock:
            if self.acquired:
                self._expire_time = time.time() + self.ttl
                return True
        return False
    
    def is_held(self):
        with self._lock:
            return self.acquired and time.time() < self._expire_time

class LockManager:
    def __init__(self):
        self.locks = {}
        self._lock = threading.Lock()
    
    def get_lock(self, lock_name, ttl=30):
        with self._lock:
            if lock_name not in self.locks:
                self.locks[lock_name] = DistributedLock(lock_name, ttl)
            return self.locks[lock_name]
    
    def acquire(self, lock_name, timeout=10, ttl=30):
        lock = self.get_lock(lock_name, ttl)
        return lock.acquire(timeout)
    
    def release(self, lock_name):
        with self._lock:
            if lock_name in self.locks:
                return self.locks[lock_name].release()
        return False

def distributed_lock(lock_name, timeout=10, ttl=30):
    def decorator(func):
        def wrapper(*args, **kwargs):
            manager = LockManager()
            if manager.acquire(lock_name, timeout, ttl):
                try:
                    return func(*args, **kwargs)
                finally:
                    manager.release(lock_name)
            else:
                raise TimeoutError(f"获取锁超时: {lock_name}")
        return wrapper
    return decorator

def main():
    @distributed_lock('resource_1', timeout=5)
    def critical_section():
        print("执行关键代码...")
        time.sleep(0.1)
        return "完成"
    
    result = critical_section()
    print(result)


if __name__ == "__main__":
    main()
