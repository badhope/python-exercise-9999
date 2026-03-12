# -----------------------------
# 题目：实现配置中心。
# -----------------------------

import json
import threading
from collections import defaultdict

class ConfigCenter:
    def __init__(self):
        self.config = {}
        self.listeners = defaultdict(list)
        self.lock = threading.Lock()
    
    def set(self, key, value):
        with self.lock:
            old_value = self.config.get(key)
            self.config[key] = value
            
            if old_value != value:
                self._notify(key, old_value, value)
    
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def get_all(self):
        with self.lock:
            return dict(self.config)
    
    def delete(self, key):
        with self.lock:
            if key in self.config:
                old_value = self.config.pop(key)
                self._notify(key, old_value, None)
    
    def subscribe(self, key, callback):
        self.listeners[key].append(callback)
    
    def _notify(self, key, old_value, new_value):
        for callback in self.listeners.get(key, []):
            try:
                callback(key, old_value, new_value)
            except Exception as e:
                print(f"Listener error: {e}")
    
    def load_from_file(self, filepath):
        with open(filepath, 'r') as f:
            data = json.load(f)
            for key, value in data.items():
                self.set(key, value)
    
    def save_to_file(self, filepath):
        with self.lock:
            with open(filepath, 'w') as f:
                json.dump(self.config, f, indent=2)

def on_config_change(key, old, new):
    print(f"Config changed: {key} = {new}")

if __name__ == "__main__":
    config = ConfigCenter()
    
    config.subscribe("debug", on_config_change)
    config.set("debug", True)
    config.set("max_connections", 100)
    config.set("debug", False)
    
    print(f"Current config: {config.get_all()}")
