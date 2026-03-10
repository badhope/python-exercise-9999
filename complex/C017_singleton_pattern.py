# -----------------------------
# 题目：单例模式实现配置管理器。
# -----------------------------

class ConfigManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._config = {}
        return cls._instance
    
    def set(self, key, value):
        self._config[key] = value
    
    def get(self, key, default=None):
        return self._config.get(key, default)
    
    def get_all(self):
        return self._config.copy()

def main():
    config1 = ConfigManager()
    config1.set("debug", True)
    config1.set("max_connections", 100)
    
    config2 = ConfigManager()
    print(f"debug: {config2.get('debug')}")
    print(f"max_connections: {config2.get('max_connections')}")
    print(f"是否同一实例: {config1 is config2}")


if __name__ == "__main__":
    main()
