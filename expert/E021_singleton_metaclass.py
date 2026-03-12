# -----------------------------
# 题目：实现元类创建单例类。
# -----------------------------

from typing import Dict, Any

class SingletonMeta(type):
    _instances: Dict[type, Any] = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class Database(metaclass=SingletonMeta):
    def __init__(self, connection_string: str = ""):
        self.connection_string = connection_string
        self.connected = False
    
    def connect(self):
        self.connected = True
        print(f"连接数据库: {self.connection_string}")
    
    def disconnect(self):
        self.connected = False
        print("断开数据库连接")

class Logger(metaclass=SingletonMeta):
    def __init__(self):
        self.logs = []
    
    def log(self, message: str):
        self.logs.append(message)
        print(f"[LOG] {message}")
    
    def get_logs(self):
        return self.logs.copy()

class ThreadSafeSingletonMeta(type):
    _instances: Dict[type, Any] = {}
    _lock = None
    
    def __call__(cls, *args, **kwargs):
        if cls._lock is None:
            import threading
            cls._lock = threading.Lock()
        
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]

class Cache(metaclass=ThreadSafeSingletonMeta):
    def __init__(self):
        self._data: Dict[str, Any] = {}
    
    def get(self, key: str) -> Any:
        return self._data.get(key)
    
    def set(self, key: str, value: Any):
        self._data[key] = value
    
    def delete(self, key: str):
        self._data.pop(key, None)

def main():
    print("=== 单例模式测试 ===")
    
    db1 = Database("mysql://localhost/db1")
    db2 = Database("mysql://localhost/db2")
    
    print(f"db1 is db2: {db1 is db2}")
    print(f"db1.connection_string: {db1.connection_string}")
    print(f"db2.connection_string: {db2.connection_string}")
    
    db1.connect()
    print(f"db2.connected: {db2.connected}")
    
    print("\n=== Logger单例 ===")
    logger1 = Logger()
    logger2 = Logger()
    
    logger1.log("消息1")
    logger2.log("消息2")
    
    print(f"logger1 is logger2: {logger1 is logger2}")
    print(f"logger1 logs: {logger1.get_logs()}")
    
    print("\n=== 线程安全单例 ===")
    cache1 = Cache()
    cache2 = Cache()
    
    cache1.set("key1", "value1")
    print(f"cache2.get('key1'): {cache2.get('key1')}")
    print(f"cache1 is cache2: {cache1 is cache2}")


if __name__ == "__main__":
    main()
