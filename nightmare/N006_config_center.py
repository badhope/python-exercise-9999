# -----------------------------
# 题目：实现简单的分布式配置中心。
# 描述：支持配置推送、版本管理、监听。
# -----------------------------

import json
import threading
import time
from collections import defaultdict

class ConfigVersion:
    def __init__(self, version, config, timestamp):
        self.version = version
        self.config = config
        self.timestamp = timestamp

class ConfigServer:
    def __init__(self):
        self.configs = {}
        self.versions = defaultdict(list)
        self.watchers = defaultdict(list)
        self._lock = threading.Lock()
        self._version_counter = 0
    
    def set_config(self, key, value, namespace='default'):
        with self._lock:
            self._version_counter += 1
            full_key = f"{namespace}:{key}"
            
            self.configs[full_key] = value
            
            version = ConfigVersion(
                self._version_counter,
                value,
                time.time()
            )
            self.versions[full_key].append(version)
            
            for callback in self.watchers[full_key]:
                callback(key, value, namespace)
    
    def get_config(self, key, namespace='default'):
        full_key = f"{namespace}:{key}"
        return self.configs.get(full_key)
    
    def get_history(self, key, namespace='default'):
        full_key = f"{namespace}:{key}"
        return self.versions.get(full_key, [])
    
    def watch(self, key, callback, namespace='default'):
        full_key = f"{namespace}:{key}"
        self.watchers[full_key].append(callback)

class ConfigClient:
    def __init__(self, server, namespace='default'):
        self.server = server
        self.namespace = namespace
        self.local_cache = {}
        self.last_sync = 0
    
    def get(self, key, default=None):
        cached = self.local_cache.get(key)
        if cached:
            return cached['value']
        
        value = self.server.get_config(key, self.namespace)
        if value is not None:
            self.local_cache[key] = {'value': value, 'timestamp': time.time()}
            return value
        return default
    
    def set(self, key, value):
        self.server.set_config(key, value, self.namespace)
        self.local_cache[key] = {'value': value, 'timestamp': time.time()}
    
    def watch(self, key, callback):
        def wrapper(k, v, ns):
            self.local_cache[key] = {'value': v, 'timestamp': time.time()}
            callback(k, v)
        
        self.server.watch(key, wrapper, self.namespace)

def main():
    server = ConfigServer()
    client = ConfigClient(server, 'production')
    
    def on_config_change(key, value):
        print(f"配置变更: {key} = {value}")
    
    client.watch('database.host', on_config_change)
    
    client.set('database.host', 'localhost')
    client.set('database.port', 3306)
    
    print(f"数据库主机: {client.get('database.host')}")
    print(f"数据库端口: {client.get('database.port')}")
    
    client.set('database.host', '192.168.1.100')


if __name__ == "__main__":
    main()
