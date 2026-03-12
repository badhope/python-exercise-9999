# -----------------------------
# 题目：实现数据库连接池。
# 描述：支持连接管理、连接复用、健康检查。
# -----------------------------

import time
import threading
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from queue import Queue, Empty
from contextlib import contextmanager
from enum import Enum

class ConnectionState(Enum):
    IDLE = "idle"
    ACTIVE = "active"
    INVALID = "invalid"

@dataclass
class ConnectionConfig:
    host: str = "localhost"
    port: int = 3306
    database: str = "test"
    username: str = "root"
    password: str = ""
    max_connections: int = 10
    min_connections: int = 2
    connection_timeout: float = 30.0
    idle_timeout: float = 300.0
    max_lifetime: float = 1800.0

@dataclass
class PooledConnection:
    conn_id: str
    connection: Any
    created_at: float = field(default_factory=time.time)
    last_used: float = field(default_factory=time.time)
    state: ConnectionState = ConnectionState.IDLE
    usage_count: int = 0

class MockConnection:
    def __init__(self, conn_id: str, config: ConnectionConfig):
        self.conn_id = conn_id
        self.config = config
        self._closed = False
        self._transaction_active = False
    
    def execute(self, sql: str, params: tuple = None) -> Dict[str, Any]:
        if self._closed:
            raise Exception("连接已关闭")
        return {
            'sql': sql,
            'params': params,
            'rows_affected': 1,
            'connection_id': self.conn_id
        }
    
    def begin_transaction(self):
        self._transaction_active = True
    
    def commit(self):
        self._transaction_active = False
    
    def rollback(self):
        self._transaction_active = False
    
    def close(self):
        self._closed = True
    
    def is_alive(self) -> bool:
        return not self._closed

class ConnectionPool:
    def __init__(
        self,
        config: ConnectionConfig,
        connection_factory: Callable = None
    ):
        self.config = config
        self.connection_factory = connection_factory or self._default_factory
        self._pool: Queue = Queue(maxsize=config.max_connections)
        self._active_connections: Dict[str, PooledConnection] = {}
        self._conn_counter = 0
        self._lock = threading.RLock()
        self._running = False
        self._maintenance_thread: Optional[threading.Thread] = None
        
        self._initialize_pool()
    
    def _default_factory(self, conn_id: str) -> Any:
        return MockConnection(conn_id, self.config)
    
    def _initialize_pool(self):
        for _ in range(self.config.min_connections):
            conn = self._create_connection()
            self._pool.put(conn)
    
    def _create_connection(self) -> PooledConnection:
        with self._lock:
            self._conn_counter += 1
            conn_id = f"conn-{self._conn_counter}"
        
        connection = self.connection_factory(conn_id)
        
        return PooledConnection(
            conn_id=conn_id,
            connection=connection
        )
    
    def get_connection(self, timeout: float = None) -> PooledConnection:
        timeout = timeout or self.config.connection_timeout
        
        try:
            pooled_conn = self._pool.get(block=True, timeout=timeout)
            
            if not self._is_connection_valid(pooled_conn):
                pooled_conn = self._create_connection()
        
        except Empty:
            if len(self._active_connections) < self.config.max_connections:
                pooled_conn = self._create_connection()
            else:
                raise Exception("连接池已满，无法获取连接")
        
        pooled_conn.state = ConnectionState.ACTIVE
        pooled_conn.last_used = time.time()
        pooled_conn.usage_count += 1
        
        with self._lock:
            self._active_connections[pooled_conn.conn_id] = pooled_conn
        
        return pooled_conn
    
    def release_connection(self, pooled_conn: PooledConnection):
        with self._lock:
            if pooled_conn.conn_id in self._active_connections:
                del self._active_connections[pooled_conn.conn_id]
        
        if self._is_connection_valid(pooled_conn):
            pooled_conn.state = ConnectionState.IDLE
            self._pool.put(pooled_conn)
        else:
            if self._pool.qsize() < self.config.min_connections:
                new_conn = self._create_connection()
                self._pool.put(new_conn)
    
    def _is_connection_valid(self, pooled_conn: PooledConnection) -> bool:
        now = time.time()
        
        if now - pooled_conn.created_at > self.config.max_lifetime:
            return False
        
        if now - pooled_conn.last_used > self.config.idle_timeout:
            return False
        
        if hasattr(pooled_conn.connection, 'is_alive'):
            if not pooled_conn.connection.is_alive():
                return False
        
        return True
    
    @contextmanager
    def connection(self):
        pooled_conn = self.get_connection()
        try:
            yield pooled_conn.connection
        finally:
            self.release_connection(pooled_conn)
    
    def start_maintenance(self, interval: float = 60.0):
        self._running = True
        self._maintenance_thread = threading.Thread(
            target=self._maintenance_loop,
            args=(interval,)
        )
        self._maintenance_thread.daemon = True
        self._maintenance_thread.start()
    
    def stop_maintenance(self):
        self._running = False
        if self._maintenance_thread:
            self._maintenance_thread.join(timeout=5.0)
    
    def _maintenance_loop(self, interval: float):
        while self._running:
            self._cleanup_invalid_connections()
            self._ensure_min_connections()
            time.sleep(interval)
    
    def _cleanup_invalid_connections(self):
        temp_list = []
        
        while not self._pool.empty():
            try:
                conn = self._pool.get_nowait()
                if self._is_connection_valid(conn):
                    temp_list.append(conn)
            except Empty:
                break
        
        for conn in temp_list:
            self._pool.put(conn)
    
    def _ensure_min_connections(self):
        current_size = self._pool.qsize()
        if current_size < self.config.min_connections:
            for _ in range(self.config.min_connections - current_size):
                conn = self._create_connection()
                self._pool.put(conn)
    
    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            return {
                'total_connections': self._pool.qsize() + len(self._active_connections),
                'active_connections': len(self._active_connections),
                'idle_connections': self._pool.qsize(),
                'max_connections': self.config.max_connections,
                'min_connections': self.config.min_connections
            }
    
    def close_all(self):
        while not self._pool.empty():
            try:
                conn = self._pool.get_nowait()
                if hasattr(conn.connection, 'close'):
                    conn.connection.close()
            except Empty:
                break
        
        with self._lock:
            for conn in self._active_connections.values():
                if hasattr(conn.connection, 'close'):
                    conn.connection.close()
            self._active_connections.clear()

def main():
    config = ConnectionConfig(
        host="localhost",
        port=3306,
        database="testdb",
        max_connections=5,
        min_connections=2
    )
    
    pool = ConnectionPool(config)
    pool.start_maintenance()
    
    print("连接池统计:", pool.get_stats())
    
    with pool.connection() as conn:
        result = conn.execute("SELECT * FROM users WHERE id = ?", (1,))
        print(f"查询结果: {result}")
    
    print("\n使用后统计:", pool.get_stats())
    
    conn1 = pool.get_connection()
    conn2 = pool.get_connection()
    print(f"\n获取两个连接后: {pool.get_stats()}")
    
    pool.release_connection(conn1)
    pool.release_connection(conn2)
    print(f"释放连接后: {pool.get_stats()}")
    
    pool.stop_maintenance()
    pool.close_all()
    print("\n连接池已关闭")

if __name__ == "__main__":
    main()
