# -----------------------------
# 题目：实现连接池。
# -----------------------------

import threading
import queue
import time

class Connection:
    def __init__(self, conn_id):
        self.conn_id = conn_id
        self.created_at = time.time()
        self.in_use = False
    
    def is_valid(self, ttl=3600):
        return time.time() - self.created_at < ttl
    
    def __enter__(self):
        self.in_use = True
        return self
    
    def __exit__(self, *args):
        self.in_use = False

class ConnectionPool:
    def __init__(self, factory, min_size=5, max_size=20, ttl=3600):
        self.factory = factory
        self.min_size = min_size
        self.max_size = max_size
        self.ttl = ttl
        
        self.pool = queue.Queue()
        self.active_connections = 0
        self.lock = threading.Lock()
        
        for _ in range(min_size):
            self._add_connection()
    
    def _add_connection(self):
        conn = self.factory()
        with self.lock:
            self.active_connections += 1
        self.pool.put(conn)
    
    def get_connection(self, timeout=10):
        try:
            conn = self.pool.get(timeout=timeout)
        except queue.Empty:
            with self.lock:
                if self.active_connections < self.max_size:
                    self._add_connection()
                    conn = self.pool.get()
                else:
                    raise Exception("Connection pool exhausted")
        
        if not conn.is_valid(self.ttl):
            conn = self.factory()
        
        return conn
    
    def return_connection(self, conn):
        if conn.in_use:
            conn.in_use = False
        self.pool.put(conn)
    
    def close_all(self):
        while not self.pool.empty():
            try:
                conn = self.pool.get_nowait()
            except queue.Empty:
                break

def create_connection():
    return Connection(id(time.time()))

if __name__ == "__main__":
    pool = ConnectionPool(create_connection, min_size=2, max_size=5)
    
    conn1 = pool.get_connection()
    print(f"Got connection {conn1.conn_id}")
    
    pool.return_connection(conn1)
    
    conn2 = pool.get_connection()
    print(f"Got connection {conn2.conn_id}")
    pool.return_connection(conn2)
