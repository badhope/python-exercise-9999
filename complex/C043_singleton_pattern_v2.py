# -----------------------------
# 题目：单例模式实现配置管理器。
# -----------------------------

class Singleton:
    _instances = {}
    
    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__new__(cls)
        return cls._instances[cls]

class ConfigManager(Singleton):
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self._config = {}
            self._env = 'development'
            self.initialized = True
    
    def set(self, key, value):
        keys = key.split('.')
        current = self._config
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value
    
    def get(self, key, default=None):
        keys = key.split('.')
        current = self._config
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        return current
    
    def set_env(self, env):
        self._env = env
    
    def get_env(self):
        return self._env
    
    def load_defaults(self):
        defaults = {
            'app.name': 'MyApp',
            'app.version': '1.0.0',
            'database.host': 'localhost',
            'database.port': 3306,
            'cache.enabled': True,
            'cache.ttl': 3600
        }
        for key, value in defaults.items():
            if self.get(key) is None:
                self.set(key, value)
    
    def get_all(self):
        return self._config.copy()

class DatabaseConnection(Singleton):
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self._connections = {}
            self.initialized = True
    
    def connect(self, name, host, port, database):
        key = f"{name}_{host}_{port}"
        if key not in self._connections:
            self._connections[key] = {
                'host': host,
                'port': port,
                'database': database,
                'connected': True
            }
        return self._connections[key]
    
    def get_connection(self, name):
        for key, conn in self._connections.items():
            if key.startswith(name + '_'):
                return conn
        return None
    
    def disconnect(self, name):
        for key in list(self._connections.keys()):
            if key.startswith(name + '_'):
                del self._connections[key]
                return True
        return False

class CacheManager(Singleton):
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self._cache = {}
            self.initialized = True
    
    def set(self, key, value, ttl=None):
        import time
        self._cache[key] = {
            'value': value,
            'expires': time.time() + ttl if ttl else None
        }
    
    def get(self, key):
        if key in self._cache:
            item = self._cache[key]
            if item['expires'] and item['expires'] < time.time():
                del self._cache[key]
                return None
            return item['value']
        return None
    
    def delete(self, key):
        if key in self._cache:
            del self._cache[key]
    
    def clear(self):
        self._cache.clear()

def main():
    print("=== 配置管理器单例测试 ===")
    config1 = ConfigManager()
    config1.set('app.name', 'TestApp')
    config1.set('database.host', '192.168.1.100')
    
    config2 = ConfigManager()
    print(f"config1 is config2: {config1 is config2}")
    print(f"从config2读取: {config2.get('app.name')}")
    print(f"数据库主机: {config2.get('database.host')}")
    
    print("\n=== 数据库连接单例测试 ===")
    db1 = DatabaseConnection()
    db1.connect('main', 'localhost', 3306, 'mydb')
    
    db2 = DatabaseConnection()
    print(f"db1 is db2: {db1 is db2}")
    print(f"从db2获取连接: {db2.get_connection('main')}")
    
    print("\n=== 缓存管理器单例测试 ===")
    cache1 = CacheManager()
    cache1.set('user:1', {'name': '张三'}, ttl=60)
    
    cache2 = CacheManager()
    print(f"cache1 is cache2: {cache1 is cache2}")
    print(f"从cache2读取: {cache2.get('user:1')}")


if __name__ == "__main__":
    main()
