# -----------------------------
# 题目：实现分布式锁。
# 描述：基于Redis风格的分布式锁实现。
# -----------------------------

import time
import uuid
import threading
from typing import Dict, Optional
from dataclasses import dataclass
from contextlib import contextmanager

@dataclass
class LockEntry:
    lock_id: str
    holder: str
    acquired_at: float
    ttl: float
    lock_type: str = 'exclusive'

class DistributedLock:
    def __init__(self, default_ttl: float = 30.0):
        self.locks: Dict[str, LockEntry] = {}
        self.wait_queues: Dict[str, List[threading.Event]] = {}
        self._lock = threading.Lock()
        self.default_ttl = default_ttl
    
    def acquire(
        self,
        resource: str,
        holder: str = None,
        ttl: float = None,
        timeout: float = 10.0,
        wait_interval: float = 0.1
    ) -> Optional[str]:
        holder = holder or str(uuid.uuid4())[:8]
        ttl = ttl or self.default_ttl
        lock_id = str(uuid.uuid4())
        start_time = time.time()
        
        while True:
            with self._lock:
                if self._try_acquire(resource, holder, lock_id, ttl):
                    return lock_id
                
                if time.time() - start_time >= timeout:
                    return None
            
            time.sleep(wait_interval)
    
    def _try_acquire(
        self,
        resource: str,
        holder: str,
        lock_id: str,
        ttl: float
    ) -> bool:
        existing = self.locks.get(resource)
        
        if existing is None:
            self.locks[resource] = LockEntry(
                lock_id=lock_id,
                holder=holder,
                acquired_at=time.time(),
                ttl=ttl
            )
            return True
        
        if time.time() - existing.acquired_at > existing.ttl:
            self.locks[resource] = LockEntry(
                lock_id=lock_id,
                holder=holder,
                acquired_at=time.time(),
                ttl=ttl
            )
            return True
        
        if existing.holder == holder:
            existing.acquired_at = time.time()
            existing.ttl = ttl
            return True
        
        return False
    
    def release(self, resource: str, lock_id: str) -> bool:
        with self._lock:
            entry = self.locks.get(resource)
            if entry and entry.lock_id == lock_id:
                del self.locks[resource]
                return True
            return False
    
    def extend(self, resource: str, lock_id: str, additional_ttl: float) -> bool:
        with self._lock:
            entry = self.locks.get(resource)
            if entry and entry.lock_id == lock_id:
                entry.ttl += additional_ttl
                return True
            return False
    
    def is_locked(self, resource: str) -> bool:
        with self._lock:
            entry = self.locks.get(resource)
            if entry is None:
                return False
            if time.time() - entry.acquired_at > entry.ttl:
                del self.locks[resource]
                return False
            return True
    
    def get_lock_info(self, resource: str) -> Optional[Dict]:
        with self._lock:
            entry = self.locks.get(resource)
            if entry is None:
                return None
            if time.time() - entry.acquired_at > entry.ttl:
                del self.locks[resource]
                return None
            return {
                'lock_id': entry.lock_id,
                'holder': entry.holder,
                'acquired_at': entry.acquired_at,
                'ttl': entry.ttl,
                'remaining_ttl': entry.ttl - (time.time() - entry.acquired_at)
            }
    
    @contextmanager
    def lock_context(
        self,
        resource: str,
        holder: str = None,
        ttl: float = None,
        timeout: float = 10.0
    ):
        lock_id = self.acquire(resource, holder, ttl, timeout)
        if lock_id is None:
            raise TimeoutError(f"获取锁超时: {resource}")
        try:
            yield lock_id
        finally:
            self.release(resource, lock_id)

class ReadWriteLock:
    def __init__(self, default_ttl: float = 30.0):
        self.default_ttl = default_ttl
        self._lock = threading.Lock()
        self.read_locks: Dict[str, Dict[str, LockEntry]] = {}
        self.write_locks: Dict[str, LockEntry] = {}
    
    def acquire_read(
        self,
        resource: str,
        holder: str = None,
        ttl: float = None,
        timeout: float = 10.0
    ) -> Optional[str]:
        holder = holder or str(uuid.uuid4())[:8]
        ttl = ttl or self.default_ttl
        lock_id = str(uuid.uuid4())
        start_time = time.time()
        
        while True:
            with self._lock:
                if resource not in self.write_locks:
                    if resource not in self.read_locks:
                        self.read_locks[resource] = {}
                    self.read_locks[resource][lock_id] = LockEntry(
                        lock_id=lock_id,
                        holder=holder,
                        acquired_at=time.time(),
                        ttl=ttl
                    )
                    return lock_id
                
                write_entry = self.write_locks[resource]
                if time.time() - write_entry.acquired_at > write_entry.ttl:
                    del self.write_locks[resource]
                    if resource not in self.read_locks:
                        self.read_locks[resource] = {}
                    self.read_locks[resource][lock_id] = LockEntry(
                        lock_id=lock_id,
                        holder=holder,
                        acquired_at=time.time(),
                        ttl=ttl
                    )
                    return lock_id
            
            if time.time() - start_time >= timeout:
                return None
            time.sleep(0.1)
    
    def acquire_write(
        self,
        resource: str,
        holder: str = None,
        ttl: float = None,
        timeout: float = 10.0
    ) -> Optional[str]:
        holder = holder or str(uuid.uuid4())[:8]
        ttl = ttl or self.default_ttl
        lock_id = str(uuid.uuid4())
        start_time = time.time()
        
        while True:
            with self._lock:
                has_readers = (
                    resource in self.read_locks and
                    len(self.read_locks[resource]) > 0
                )
                has_writer = resource in self.write_locks
                
                if not has_readers and not has_writer:
                    self.write_locks[resource] = LockEntry(
                        lock_id=lock_id,
                        holder=holder,
                        acquired_at=time.time(),
                        ttl=ttl
                    )
                    return lock_id
            
            if time.time() - start_time >= timeout:
                return None
            time.sleep(0.1)
    
    def release_read(self, resource: str, lock_id: str) -> bool:
        with self._lock:
            if resource in self.read_locks and lock_id in self.read_locks[resource]:
                del self.read_locks[resource][lock_id]
                if not self.read_locks[resource]:
                    del self.read_locks[resource]
                return True
            return False
    
    def release_write(self, resource: str, lock_id: str) -> bool:
        with self._lock:
            if resource in self.write_locks:
                entry = self.write_locks[resource]
                if entry.lock_id == lock_id:
                    del self.write_locks[resource]
                    return True
            return False

def main():
    lock_manager = DistributedLock()
    
    lock_id = lock_manager.acquire("resource-1", "client-A", ttl=5.0)
    print(f"获取锁: {lock_id}")
    
    print(f"资源是否锁定: {lock_manager.is_locked('resource-1')}")
    print(f"锁信息: {lock_manager.get_lock_info('resource-1')}")
    
    lock_id2 = lock_manager.acquire("resource-1", "client-B", timeout=2.0)
    print(f"另一个客户端获取锁: {lock_id2}")
    
    released = lock_manager.release("resource-1", lock_id)
    print(f"释放锁: {released}")
    
    lock_id3 = lock_manager.acquire("resource-1", "client-B", timeout=2.0)
    print(f"再次获取锁: {lock_id3}")
    
    with lock_manager.lock_context("resource-2", ttl=5.0) as ctx_lock_id:
        print(f"上下文管理器获取锁: {ctx_lock_id}")
        print(f"资源2是否锁定: {lock_manager.is_locked('resource-2')}")

if __name__ == "__main__":
    main()
