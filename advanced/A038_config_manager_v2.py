# -----------------------------
# 题目：实现简单的配置管理器。
# -----------------------------

import json
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ConfigSource:
    name: str
    priority: int
    data: Dict[str, Any]

class ConfigManager:
    def __init__(self):
        self._sources: List[ConfigSource] = []
        self._cache: Dict[str, Any] = {}
        self._watchers: Dict[str, List[callable]] = {}
    
    def add_source(self, name: str, data: Dict[str, Any], priority: int = 0):
        source = ConfigSource(name=name, priority=priority, data=data)
        self._sources.append(source)
        self._sources.sort(key=lambda s: s.priority, reverse=True)
        self._invalidate_cache()
    
    def add_file_source(self, filepath: str, priority: int = 0) -> bool:
        path = Path(filepath)
        if not path.exists():
            return False
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                if path.suffix == '.json':
                    data = json.load(f)
                else:
                    data = {}
            
            self.add_source(f"file:{filepath}", data, priority)
            return True
        except Exception:
            return False
    
    def add_env_source(self, prefix: str = '', priority: int = 100):
        data = {}
        for key, value in os.environ.items():
            if prefix:
                if key.startswith(prefix):
                    config_key = key[len(prefix):].lower()
                    data[config_key] = self._parse_env_value(value)
            else:
                data[key.lower()] = self._parse_env_value(value)
        
        self.add_source('environment', data, priority)
    
    def _parse_env_value(self, value: str) -> Any:
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        try:
            return int(value)
        except ValueError:
            pass
        
        try:
            return float(value)
        except ValueError:
            pass
        
        return value
    
    def get(self, key: str, default: Any = None) -> Any:
        if key in self._cache:
            return self._cache[key]
        
        keys = key.split('.')
        
        for source in self._sources:
            value = self._get_nested(source.data, keys)
            if value is not None:
                self._cache[key] = value
                return value
        
        return default
    
    def _get_nested(self, data: Dict, keys: List[str]) -> Any:
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current
    
    def set(self, key: str, value: Any):
        keys = key.split('.')
        
        if not self._sources:
            self.add_source('default', {})
        
        target = self._sources[-1].data
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        
        target[keys[-1]] = value
        self._invalidate_cache()
        self._notify_watchers(key, value)
    
    def _invalidate_cache(self):
        self._cache.clear()
    
    def watch(self, key: str, callback: callable):
        if key not in self._watchers:
            self._watchers[key] = []
        self._watchers[key].append(callback)
    
    def _notify_watchers(self, key: str, value: Any):
        for watched_key, callbacks in self._watchers.items():
            if key == watched_key or key.startswith(watched_key + '.'):
                for callback in callbacks:
                    try:
                        callback(key, value)
                    except Exception as e:
                        print(f"配置监听器错误: {e}")
    
    def get_all(self) -> Dict[str, Any]:
        result = {}
        for source in reversed(self._sources):
            self._deep_merge(result, source.data)
        return result
    
    def _deep_merge(self, target: Dict, source: Dict):
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value

class ConfigBuilder:
    def __init__(self):
        self.manager = ConfigManager()
    
    def with_defaults(self, defaults: Dict[str, Any]) -> 'ConfigBuilder':
        self.manager.add_source('defaults', defaults, priority=0)
        return self
    
    def with_file(self, filepath: str) -> 'ConfigBuilder':
        self.manager.add_file_source(filepath, priority=50)
        return self
    
    def with_env(self, prefix: str = '') -> 'ConfigBuilder':
        self.manager.add_env_source(prefix, priority=100)
        return self
    
    def build(self) -> ConfigManager:
        return self.manager

def main():
    print("=== 构建配置管理器 ===")
    config = (ConfigBuilder()
              .with_defaults({
                  'app': {'name': 'MyApp', 'debug': False},
                  'database': {'host': 'localhost', 'port': 3306}
              })
              .build())
    
    print(f"应用名称: {config.get('app.name')}")
    print(f"数据库主机: {config.get('database.host')}")
    print(f"数据库端口: {config.get('database.port')}")
    
    print("\n=== 修改配置 ===")
    config.set('app.debug', True)
    print(f"调试模式: {config.get('app.debug')}")
    
    print("\n=== 配置监听 ===")
    def on_config_change(key, value):
        print(f"配置变更: {key} = {value}")
    
    config.watch('app', on_config_change)
    config.set('app.version', '1.0.0')
    
    print("\n=== 获取所有配置 ===")
    all_config = config.get_all()
    for key, value in all_config.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
