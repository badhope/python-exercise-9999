# -----------------------------
# 题目：实现简单的分布式锁。
# -----------------------------

import time
import uuid
import threading

class DistributedLock:
    def __init__(self, name):
        self.name = name
        self.lock = threading.Lock()
        self.holders = set()
    
    def acquire(self, holder_id, timeout=10):
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.lock.acquire(blocking=False):
                self.holders.add(holder_id)
                return True
            time.sleep(0.1)
        return False
    
    def release(self, holder_id):
        if holder_id in self.holders:
            self.holders.remove(holder_id)
            self.lock.release()
            return True
        return False
    
    def is_locked(self):
        return self.lock.locked()

def worker(lock, worker_id):
    if lock.acquire(worker_id):
        print(f"[{worker_id}] 获取锁成功")
        time.sleep(1)
        lock.release(worker_id)
        print(f"[{worker_id}] 释放锁")
    else:
        print(f"[{worker_id}] 获取锁失败")

def main():
    lock = DistributedLock("my_resource")
    threads = []
    for i in range(3):
        t = threading.Thread(target=worker, args=(lock, f"worker-{i}"))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()


if __name__ == "__main__":
    main()
