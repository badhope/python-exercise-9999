# -----------------------------
# 题目：实现简单的配置中心。
# 描述：支持配置热更新、环境隔离。
# -----------------------------

import json
import os
from threading import Lock

class ConfigCenter:
    def __init__(self):
        self._configs = {}
        self._watchers = {}
        self._lock = Lock()
        self._env = os.getenv('ENV', 'development')
    
    def load(self, config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        with self._lock:
            base_config = config.get('default', {})
            env_config = config.get(self._env, {})
            self._configs = {**base_config, **env_config}
    
    def get(self, key, default=None):
        with self._lock:
            keys = key.split('.')
            value = self._configs
            for k in keys:
                if isinstance(value, dict):
                    value = value.get(k)
                else:
                    return default
            return value if value is not None else default
    
    def set(self, key, value):
        with self._lock:
            keys = key.split('.')
            config = self._configs
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            config[keys[-1]] = value
        self._notify_watchers(key)
    
    def watch(self, key, callback):
        with self._lock:
            if key not in self._watchers:
                self._watchers[key] = []
            self._watchers[key].append(callback)
    
    def _notify_watchers(self, key):
        if key in self._watchers:
            for callback in self._watchers[key]:
                callback(self.get(key))
    
    def get_env(self):
        return self._env

def main():
    config = ConfigCenter()
    
    config._configs = {
        'database': {
            'host': 'localhost',
            'port': 3306
        },
        'debug': True
    }
    
    print(f"数据库主机: {config.get('database.host')}")
    print(f"调试模式: {config.get('debug')}")
    
    def on_debug_change(value):
        print(f"调试模式变更为: {value}")
    
    config.watch('debug', on_debug_change)
    config.set('debug', False)


if __name__ == "__main__":
    main()
