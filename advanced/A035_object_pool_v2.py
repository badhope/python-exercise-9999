# -----------------------------
# 题目：实现简单的对象池。
# -----------------------------

from typing import Type, Callable, List, Optional, Any
from dataclasses import dataclass
from threading import Lock
import time

@dataclass
class PoolObject:
    id: int
    created_at: float
    last_used: float
    in_use: bool = False
    
    def reset(self):
        pass

class ObjectPool:
    def __init__(self, 
                 object_class: Type,
                 factory: Callable = None,
                 reset_func: Callable = None,
                 max_size: int = 10,
                 initial_size: int = 2):
        self.object_class = object_class
        self.factory = factory or object_class
        self.reset_func = reset_func
        self.max_size = max_size
        
        self._pool: List[Any] = []
        self._available: List[Any] = []
        self._lock = Lock()
        self._next_id = 1
        
        self._initialize(initial_size)
    
    def _initialize(self, initial_size: int):
        for _ in range(initial_size):
            obj = self._create_object()
            self._pool.append(obj)
            self._available.append(obj)
    
    def _create_object(self) -> Any:
        with self._lock:
            obj_id = self._next_id
            self._next_id += 1
        
        obj = self.factory()
        
        if hasattr(obj, 'id'):
            obj.id = obj_id
        if hasattr(obj, 'created_at'):
            obj.created_at = time.time()
        if hasattr(obj, 'last_used'):
            obj.last_used = time.time()
        
        return obj
    
    def acquire(self) -> Optional[Any]:
        with self._lock:
            if self._available:
                obj = self._available.pop()
                obj.in_use = True
                if hasattr(obj, 'last_used'):
                    obj.last_used = time.time()
                return obj
            
            if len(self._pool) < self.max_size:
                obj = self._create_object()
                obj.in_use = True
                self._pool.append(obj)
                return obj
        
        return None
    
    def release(self, obj: Any):
        if self.reset_func:
            self.reset_func(obj)
        elif hasattr(obj, 'reset'):
            obj.reset()
        
        with self._lock:
            if obj in self._pool:
                obj.in_use = False
                if obj not in self._available:
                    self._available.append(obj)
    
    def get_stats(self) -> dict:
        with self._lock:
            total = len(self._pool)
            available = len(self._available)
        
        return {
            'total': total,
            'available': available,
            'in_use': total - available,
            'max': self.max_size
        }
    
    def clear(self):
        with self._lock:
            self._pool.clear()
            self._available.clear()

class DatabaseConnection:
    def __init__(self):
        self.id = 0
        self.created_at = 0
        self.last_used = 0
        self.in_use = False
        self.query_count = 0
    
    def execute(self, sql: str):
        self.query_count += 1
        return f"执行: {sql}"
    
    def reset(self):
        self.query_count = 0

class StringBuilder:
    def __init__(self):
        self.id = 0
        self.created_at = 0
        self.last_used = 0
        self.in_use = False
        self._buffer = []
    
    def append(self, text: str):
        self._buffer.append(text)
    
    def build(self) -> str:
        return ''.join(self._buffer)
    
    def reset(self):
        self._buffer.clear()

class PoolManager:
    def __init__(self):
        self._pools: dict = {}
    
    def register(self, name: str, pool: ObjectPool):
        self._pools[name] = pool
    
    def get_pool(self, name: str) -> Optional[ObjectPool]:
        return self._pools.get(name)
    
    def acquire(self, pool_name: str) -> Optional[Any]:
        pool = self._pools.get(pool_name)
        if pool:
            return pool.acquire()
        return None
    
    def release(self, pool_name: str, obj: Any):
        pool = self._pools.get(pool_name)
        if pool:
            pool.release(obj)
    
    def get_all_stats(self) -> dict:
        return {name: pool.get_stats() for name, pool in self._pools.items()}

def main():
    print("=== 数据库连接池 ===")
    db_pool = ObjectPool(
        object_class=DatabaseConnection,
        max_size=5,
        initial_size=2
    )
    
    conn1 = db_pool.acquire()
    conn2 = db_pool.acquire()
    print(f"获取2个连接: {db_pool.get_stats()}")
    
    if conn1:
        print(f"连接1执行: {conn1.execute('SELECT * FROM users')}")
    
    db_pool.release(conn1)
    print(f"释放1个连接: {db_pool.get_stats()}")
    
    print("\n=== 字符串构建器池 ===")
    sb_pool = ObjectPool(
        object_class=StringBuilder,
        max_size=3,
        initial_size=1
    )
    
    builder = sb_pool.acquire()
    if builder:
        builder.append("Hello")
        builder.append(" ")
        builder.append("World")
        print(f"构建结果: {builder.build()}")
        sb_pool.release(builder)
    
    print(f"池状态: {sb_pool.get_stats()}")
    
    print("\n=== PoolManager ===")
    manager = PoolManager()
    manager.register('database', db_pool)
    manager.register('string_builder', sb_pool)
    
    print("所有池状态:")
    for name, stats in manager.get_all_stats().items():
        print(f"  {name}: {stats}")


if __name__ == "__main__":
    main()
