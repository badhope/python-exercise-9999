# -----------------------------
# 题目：实现简单的连接池。
# -----------------------------

import threading
import time
from queue import Queue, Empty
from typing import Any, Callable, Optional
from dataclasses import dataclass

@dataclass
class Connection:
    id: int
    created_at: float
    last_used: float
    is_active: bool = True
    
    def is_expired(self, max_age: float) -> bool:
        return time.time() - self.created_at > max_age
    
    def is_idle_too_long(self, max_idle: float) -> bool:
        return time.time() - self.last_used > max_idle

class ConnectionPool:
    def __init__(self, 
                 create_func: Callable,
                 close_func: Callable = None,
                 max_connections: int = 10,
                 min_connections: int = 2,
                 max_age: float = 3600,
                 max_idle: float = 600):
        self.create_func = create_func
        self.close_func = close_func
        self.max_connections = max_connections
        self.min_connections = min_connections
        self.max_age = max_age
        self.max_idle = max_idle
        
        self._pool: Queue = Queue()
        self._all_connections: dict = {}
        self._lock = threading.Lock()
        self._next_id = 1
        
        self._initialize()
    
    def _initialize(self):
        for _ in range(self.min_connections):
            conn = self._create_connection()
            self._pool.put(conn)
    
    def _create_connection(self) -> Connection:
        with self._lock:
            conn_id = self._next_id
            self._next_id += 1
        
        raw_conn = self.create_func()
        conn = Connection(
            id=conn_id,
            created_at=time.time(),
            last_used=time.time()
        )
        conn.raw = raw_conn
        
        with self._lock:
            self._all_connections[conn_id] = conn
        
        return conn
    
    def get(self, timeout: float = 5) -> Optional[Connection]:
        try:
            conn = self._pool.get(timeout=timeout)
            if not conn.is_active or conn.is_expired(self.max_age):
                self._close_connection(conn)
                return self._create_and_get()
            
            conn.last_used = time.time()
            return conn
        except Empty:
            with self._lock:
                if len(self._all_connections) < self.max_connections:
                    return self._create_connection()
            return None
    
    def _create_and_get(self) -> Connection:
        conn = self._create_connection()
        conn.last_used = time.time()
        return conn
    
    def release(self, conn: Connection):
        if not conn.is_active:
            self._close_connection(conn)
            return
        
        if conn.is_expired(self.max_age):
            self._close_connection(conn)
            self._ensure_min_connections()
            return
        
        self._pool.put(conn)
    
    def _close_connection(self, conn: Connection):
        conn.is_active = False
        with self._lock:
            if conn.id in self._all_connections:
                del self._all_connections[conn.id]
        
        if self.close_func and hasattr(conn, 'raw'):
            try:
                self.close_func(conn.raw)
            except Exception:
                pass
    
    def _ensure_min_connections(self):
        with self._lock:
            current = len(self._all_connections)
        
        for _ in range(self.min_connections - current):
            conn = self._create_connection()
            self._pool.put(conn)
    
    def close_all(self):
        while not self._pool.empty():
            try:
                conn = self._pool.get_nowait()
                self._close_connection(conn)
            except Empty:
                break
    
    def get_stats(self) -> dict:
        with self._lock:
            total = len(self._all_connections)
            available = self._pool.qsize()
        
        return {
            'total': total,
            'available': available,
            'in_use': total - available,
            'max': self.max_connections
        }

class DatabaseConnectionPool(ConnectionPool):
    def __init__(self, connection_string: str, **kwargs):
        self.connection_string = connection_string
        super().__init__(
            create_func=self._create_db_connection,
            close_func=self._close_db_connection,
            **kwargs
        )
    
    def _create_db_connection(self):
        return {'connection_string': self.connection_string, 'connected': True}
    
    def _close_db_connection(self, conn):
        conn['connected'] = False

def main():
    def create_mock_connection():
        return {'connected': True, 'id': id(object())}
    
    def close_mock_connection(conn):
        conn['connected'] = False
    
    pool = ConnectionPool(
        create_func=create_mock_connection,
        close_func=close_mock_connection,
        max_connections=5,
        min_connections=2
    )
    
    print("=== 初始状态 ===")
    print(pool.get_stats())
    
    print("\n=== 获取连接 ===")
    conn1 = pool.get()
    conn2 = pool.get()
    print(f"获取2个连接后: {pool.get_stats()}")
    
    print("\n=== 释放连接 ===")
    pool.release(conn1)
    print(f"释放1个连接后: {pool.get_stats()}")
    
    print("\n=== 获取更多连接 ===")
    connections = []
    for _ in range(4):
        conn = pool.get(timeout=1)
        if conn:
            connections.append(conn)
    print(f"尝试获取4个连接后: {pool.get_stats()}")
    
    print("\n=== 释放所有连接 ===")
    for conn in connections:
        pool.release(conn)
    pool.release(conn2)
    print(f"释放后: {pool.get_stats()}")
    
    pool.close_all()
    print(f"\n关闭所有后: {pool.get_stats()}")


if __name__ == "__main__":
    main()
