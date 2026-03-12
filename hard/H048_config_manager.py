# -----------------------------
# 题目：实现简单的配置管理系统。
# 描述：管理应用配置、环境变量、版本控制等。
# -----------------------------

from datetime import datetime
import json

class Config:
    def __init__(self, config_id, name, environment):
        self.id = config_id
        self.name = name
        self.environment = environment
        self.data = {}
        self.version = 1
        self.history = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def set(self, key, value):
        old_value = self.data.get(key)
        self.data[key] = value
        self.version += 1
        self.updated_at = datetime.now()
        self.history.append({
            'action': 'set',
            'key': key,
            'old_value': old_value,
            'new_value': value,
            'version': self.version - 1,
            'timestamp': datetime.now()
        })
    
    def get(self, key, default=None):
        return self.data.get(key, default)
    
    def delete(self, key):
        if key in self.data:
            old_value = self.data[key]
            del self.data[key]
            self.version += 1
            self.updated_at = datetime.now()
            self.history.append({
                'action': 'delete',
                'key': key,
                'old_value': old_value,
                'version': self.version - 1,
                'timestamp': datetime.now()
            })
            return True
        return False
    
    def get_all(self):
        return dict(self.data)
    
    def to_json(self):
        return json.dumps(self.data, indent=2, ensure_ascii=False)

class ConfigManager:
    def __init__(self):
        self.configs = {}
        self.next_id = 1
    
    def create_config(self, name, environment="default"):
        config = Config(self.next_id, name, environment)
        self.configs[self.next_id] = config
        self.next_id += 1
        return config.id
    
    def get_config(self, config_id):
        return self.configs.get(config_id)
    
    def set_value(self, config_id, key, value):
        config = self.configs.get(config_id)
        if config:
            config.set(key, value)
            return True
        return False
    
    def get_value(self, config_id, key, default=None):
        config = self.configs.get(config_id)
        if config:
            return config.get(key, default)
        return default
    
    def delete_key(self, config_id, key):
        config = self.configs.get(config_id)
        if config:
            return config.delete(key)
        return False
    
    def get_configs_by_env(self, environment):
        return [c for c in self.configs.values() if c.environment == environment]
    
    def import_config(self, config_id, json_str):
        config = self.configs.get(config_id)
        if config:
            try:
                data = json.loads(json_str)
                for key, value in data.items():
                    config.set(key, value)
                return True
            except json.JSONDecodeError:
                return False
        return False
    
    def export_config(self, config_id):
        config = self.configs.get(config_id)
        if config:
            return config.to_json()
        return None
    
    def get_config_history(self, config_id):
        config = self.configs.get(config_id)
        if config:
            return config.history
        return []
    
    def compare_configs(self, config_id1, config_id2):
        config1 = self.configs.get(config_id1)
        config2 = self.configs.get(config_id2)
        
        if not config1 or not config2:
            return None
        
        all_keys = set(config1.data.keys()) | set(config2.data.keys())
        diff = []
        
        for key in all_keys:
            val1 = config1.data.get(key)
            val2 = config2.data.get(key)
            
            if val1 != val2:
                diff.append({
                    'key': key,
                    'config1_value': val1,
                    'config2_value': val2
                })
        
        return diff
    
    def get_stats(self):
        return {
            'total_configs': len(self.configs),
            'environments': len(set(c.environment for c in self.configs.values())),
            'total_keys': sum(len(c.data) for c in self.configs.values())
        }

def main():
    manager = ConfigManager()
    
    c1 = manager.create_config("app_config", "production")
    c2 = manager.create_config("app_config", "development")
    
    manager.set_value(c1, "database_host", "prod.db.example.com")
    manager.set_value(c1, "database_port", 5432)
    manager.set_value(c1, "debug", False)
    
    manager.set_value(c2, "database_host", "localhost")
    manager.set_value(c2, "database_port", 5432)
    manager.set_value(c2, "debug", True)
    
    print("配置管理统计:")
    stats = manager.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print(f"\n配置{c1}内容:")
    config = manager.get_config(c1)
    for key, value in config.get_all().items():
        print(f"  {key}: {value}")
    
    print("\n配置差异:")
    diff = manager.compare_configs(c1, c2)
    for item in diff:
        print(f"  {item['key']}: {item['config1_value']} vs {item['config2_value']}")


if __name__ == "__main__":
    main()
