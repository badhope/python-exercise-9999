# -----------------------------
# 题目：实现简单的连接池。
# 描述：管理数据库连接的获取和释放。
# -----------------------------

import queue
import time
import threading

class Connection:
    def __init__(self, conn_id):
        self.conn_id = conn_id
        self.created_at = time.time()
    
    def execute(self, query):
        return f"[Connection-{self.conn_id}] 执行: {query}"
    
    def close(self):
        pass

class ConnectionPool:
    def __init__(self, max_connections=10):
        self.max_connections = max_connections
        self.pool = queue.Queue(max_connections)
        self.lock = threading.Lock()
        self.created = 0
    
    def get_connection(self):
        if not self.pool.empty():
            return self.pool.get()
        
        with self.lock:
            if self.created < self.max_connections:
                self.created += 1
                return Connection(self.created)
        
        return self.pool.get()
    
    def release_connection(self, conn):
        self.pool.put(conn)
    
    def get_pool_size(self):
        return self.pool.qsize()

def main():
    pool = ConnectionPool(5)
    conn1 = pool.get_connection()
    conn2 = pool.get_connection()
    print(conn1.execute("SELECT * FROM users"))
    print(conn2.execute("SELECT * FROM orders"))
    pool.release_connection(conn1)
    pool.release_connection(conn2)
    print(f"池中连接数: {pool.get_pool_size()}")


if __name__ == "__main__":
    main()
