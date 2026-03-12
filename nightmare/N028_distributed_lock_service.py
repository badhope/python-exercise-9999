# -----------------------------
# 题目：实现分布式锁服务。
# 描述：支持锁获取、锁续期、锁释放、死锁检测。
# -----------------------------

import time
import threading
import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from queue import Queue

class LockStatus(Enum):
    ACQUIRED = "acquired"
    WAITING = "waiting"
    RELEASED = "released"
    EXPIRED = "expired"

@dataclass
class Lock:
    lock_key: str
    lock_id: str
    owner_id: str
    acquired_at: float
    expire_at: float
    status: LockStatus = LockStatus.ACQUIRED
    waiters: List[str] = field(default_factory=list)
    reentrant_count: int = 1

class DistributedLockService:
    def __init__(self, default_ttl: float = 30.0):
        self.locks: Dict[str, Lock] = {}
        self.default_ttl = default_ttl
        self._lock = threading.RLock()
        self._running = False
        self._watcher_thread: Optional[threading.Thread] = None
    
    def acquire(
        self,
        lock_key: str,
        owner_id: str,
        ttl: float = None,
        timeout: float = 0
    ) -> Optional[str]:
        ttl = ttl or self.default_ttl
        lock_id = f"lock-{uuid.uuid4().hex[:12]}"
        start_time = time.time()
        
        while True:
            with self._lock:
                existing_lock = self.locks.get(lock_key)
                
                if existing_lock is None or existing_lock.expire_at < time.time():
                    lock = Lock(
                        lock_key=lock_key,
                        lock_id=lock_id,
                        owner_id=owner_id,
                        acquired_at=time.time(),
                        expire_at=time.time() + ttl
                    )
                    self.locks[lock_key] = lock
                    return lock_id
                
                if existing_lock.owner_id == owner_id:
                    existing_lock.reentrant_count += 1
                    existing_lock.expire_at = time.time() + ttl
                    return existing_lock.lock_id
                
                if timeout == 0:
                    return None
                
                existing_lock.waiters.append(owner_id)
            
            if time.time() - start_time >= timeout:
                with self._lock:
                    if lock_key in self.locks:
                        self.locks[lock_key].waiters.remove(owner_id)
                return None
            
            time.sleep(0.1)
    
    def release(self, lock_key: str, lock_id: str, owner_id: str) -> bool:
        with self._lock:
            lock = self.locks.get(lock_key)
            
            if lock is None:
                return False
            
            if lock.lock_id != lock_id or lock.owner_id != owner_id:
                return False
            
            lock.reentrant_count -= 1
            
            if lock.reentrant_count <= 0:
                del self.locks[lock_key]
            
            return True
    
    def renew(self, lock_key: str, lock_id: str, owner_id: str, ttl: float = None) -> bool:
        ttl = ttl or self.default_ttl
        
        with self._lock:
            lock = self.locks.get(lock_key)
            
            if lock is None:
                return False
            
            if lock.lock_id != lock_id or lock.owner_id != owner_id:
                return False
            
            lock.expire_at = time.time() + ttl
            return True
    
    def is_locked(self, lock_key: str) -> bool:
        with self._lock:
            lock = self.locks.get(lock_key)
            if lock:
                return lock.expire_at > time.time()
            return False
    
    def get_lock_info(self, lock_key: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            lock = self.locks.get(lock_key)
            if lock:
                return {
                    'lock_key': lock.lock_key,
                    'lock_id': lock.lock_id,
                    'owner_id': lock.owner_id,
                    'acquired_at': lock.acquired_at,
                    'expire_at': lock.expire_at,
                    'reentrant_count': lock.reentrant_count,
                    'waiters': len(lock.waiters)
                }
            return None
    
    def start_watcher(self, interval: float = 1.0):
        self._running = True
        self._watcher_thread = threading.Thread(
            target=self._watch_loop,
            args=(interval,)
        )
        self._watcher_thread.daemon = True
        self._watcher_thread.start()
    
    def stop_watcher(self):
        self._running = False
        if self._watcher_thread:
            self._watcher_thread.join(timeout=5.0)
    
    def _watch_loop(self, interval: float):
        while self._running:
            self._cleanup_expired_locks()
            time.sleep(interval)
    
    def _cleanup_expired_locks(self):
        now = time.time()
        with self._lock:
            expired_keys = [
                key for key, lock in self.locks.items()
                if lock.expire_at < now
            ]
            
            for key in expired_keys:
                del self.locks[key]
    
    def detect_deadlocks(self) -> List[Dict[str, Any]]:
        with self._lock:
            deadlocks = []
            
            for lock in self.locks.values():
                if lock.waiters:
                    for waiter in lock.waiters:
                        for other_lock in self.locks.values():
                            if other_lock.owner_id == waiter:
                                if lock.owner_id in other_lock.waiters:
                                    deadlocks.append({
                                        'lock1': lock.lock_key,
                                        'lock2': other_lock.lock_key,
                                        'owner1': lock.owner_id,
                                        'owner2': other_lock.owner_id
                                    })
            
            return deadlocks

class DistributedLock:
    def __init__(self, service: DistributedLockService, lock_key: str, owner_id: str):
        self.service = service
        self.lock_key = lock_key
        self.owner_id = owner_id
        self.lock_id: Optional[str] = None
        self._renew_thread: Optional[threading.Thread] = None
        self._renewing = False
    
    def acquire(self, ttl: float = None, timeout: float = 0) -> bool:
        self.lock_id = self.service.acquire(
            self.lock_key,
            self.owner_id,
            ttl=ttl,
            timeout=timeout
        )
        return self.lock_id is not None
    
    def release(self) -> bool:
        if self.lock_id is None:
            return False
        
        self._stop_renew()
        return self.service.release(self.lock_key, self.lock_id, self.owner_id)
    
    def start_auto_renew(self, ttl: float = 30.0):
        self._renewing = True
        self._renew_thread = threading.Thread(
            target=self._renew_loop,
            args=(ttl,)
        )
        self._renew_thread.daemon = True
        self._renew_thread.start()
    
    def _stop_renew(self):
        self._renewing = False
        if self._renew_thread:
            self._renew_thread.join(timeout=1.0)
    
    def _renew_loop(self, ttl: float):
        while self._renewing and self.lock_id:
            time.sleep(ttl / 3)
            if self._renewing:
                self.service.renew(self.lock_key, self.lock_id, self.owner_id, ttl)
    
    def __enter__(self):
        self.acquire()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

def main():
    service = DistributedLockService(default_ttl=10.0)
    service.start_watcher()
    
    print("获取锁...")
    lock1 = DistributedLock(service, "resource-1", "client-1")
    lock2 = DistributedLock(service, "resource-2", "client-2")
    
    if lock1.acquire():
        print("client-1 获取 resource-1 成功")
    
    if lock2.acquire():
        print("client-2 获取 resource-2 成功")
    
    print("\n尝试获取已锁定的资源...")
    lock1_dup = DistributedLock(service, "resource-1", "client-3")
    if not lock1_dup.acquire(timeout=1.0):
        print("client-3 获取 resource-1 失败 (已锁定)")
    
    print("\n锁信息:")
    info = service.get_lock_info("resource-1")
    if info:
        print(f"  resource-1: owner={info['owner_id']}, reentrant={info['reentrant_count']}")
    
    print("\n释放锁...")
    lock1.release()
    print("client-1 释放 resource-1")
    
    if lock1_dup.acquire():
        print("client-3 获取 resource-1 成功")
        lock1_dup.release()
    
    lock2.release()
    
    print("\n死锁检测:")
    deadlocks = service.detect_deadlocks()
    print(f"  检测到 {len(deadlocks)} 个死锁")
    
    service.stop_watcher()

if __name__ == "__main__":
    main()
