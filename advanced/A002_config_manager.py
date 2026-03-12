# -----------------------------
# 题目：实现简单的配置管理。
# 描述：支持从文件、环境变量加载配置。
# -----------------------------

import os
import json

class Config:
    def __init__(self):
        self._config = {}
    
    def load_from_dict(self, config_dict):
        self._config.update(config_dict)
    
    def load_from_file(self, filepath):
        with open(filepath, 'r') as f:
            self._config.update(json.load(f))
    
    def load_from_env(self, prefix="APP_"):
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower()
                self._config[config_key] = value
    
    def get(self, key, default=None):
        return self._config.get(key, default)
    
    def set(self, key, value):
        self._config[key] = value
    
    def __getitem__(self, key):
        return self._config[key]
    
    def __setitem__(self, key, value):
        self._config[key] = value

def main():
    config = Config()
    config.load_from_dict({"debug": True, "host": "localhost"})
    config.load_from_env("APP_")
    print(f"Host: {config.get('host')}")
    print(f"Debug: {config.get('debug')}")


if __name__ == "__main__":
    main()
