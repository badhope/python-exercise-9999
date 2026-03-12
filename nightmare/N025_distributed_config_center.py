# -----------------------------
# 题目：实现分布式配置中心。
# 描述：支持配置管理、版本控制、热更新。
# -----------------------------

import time
import threading
import json
import hashlib
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class ConfigStatus(Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ROLLED_BACK = "rolled_back"

@dataclass
class ConfigVersion:
    version: int
    config: Dict[str, Any]
    checksum: str
    created_at: float
    created_by: str
    status: ConfigStatus = ConfigStatus.ACTIVE
    description: str = ""

@dataclass
class ConfigChange:
    key: str
    old_value: Any
    new_value: Any
    change_type: str

class ConfigHistory:
    def __init__(self):
        self.versions: List[ConfigVersion] = []
        self._current_version = 0
    
    def add(self, config: Dict[str, Any], created_by: str, description: str = "") -> ConfigVersion:
        self._current_version += 1
        checksum = self._calculate_checksum(config)
        
        version = ConfigVersion(
            version=self._current_version,
            config=config.copy(),
            checksum=checksum,
            created_at=time.time(),
            created_by=created_by,
            description=description
        )
        
        self.versions.append(version)
        return version
    
    def get_version(self, version: int) -> Optional[ConfigVersion]:
        for v in self.versions:
            if v.version == version:
                return v
        return None
    
    def get_latest(self) -> Optional[ConfigVersion]:
        if self.versions:
            return self.versions[-1]
        return None
    
    def _calculate_checksum(self, config: Dict[str, Any]) -> str:
        return hashlib.md5(json.dumps(config, sort_keys=True).encode()).hexdigest()

class ConfigWatcher:
    def __init__(self):
        self._watchers: Dict[str, List[Callable]] = {}
        self._lock = threading.Lock()
    
    def watch(self, key: str, callback: Callable[[str, Any, Any], None]):
        with self._lock:
            if key not in self._watchers:
                self._watchers[key] = []
            self._watchers[key].append(callback)
    
    def unwatch(self, key: str, callback: Callable = None):
        with self._lock:
            if callback:
                if key in self._watchers:
                    self._watchers[key] = [
                        cb for cb in self._watchers[key] if cb != callback
                    ]
            else:
                self._watchers.pop(key, None)
    
    def notify(self, key: str, old_value: Any, new_value: Any):
        with self._lock:
            callbacks = self._watchers.get(key, [])
            callbacks.extend(self._watchers.get("*", []))
        
        for callback in callbacks:
            try:
                callback(key, old_value, new_value)
            except Exception:
                pass

class ConfigNamespace:
    def __init__(self, name: str):
        self.name = name
        self.config: Dict[str, Any] = {}
        self.history = ConfigHistory()
        self.watcher = ConfigWatcher()
        self._lock = threading.RLock()
    
    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            keys = key.split(".")
            value = self.config
            
            for k in keys:
                if isinstance(value, dict):
                    value = value.get(k)
                else:
                    return default
            
            return value if value is not None else default
    
    def set(self, key: str, value: Any, updated_by: str = "system") -> bool:
        with self._lock:
            old_value = self.get(key)
            
            keys = key.split(".")
            current = self.config
            
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            
            current[keys[-1]] = value
            
            self.history.add(self.config, updated_by, f"Updated {key}")
            
            self.watcher.notify(key, old_value, value)
            
            return True
    
    def delete(self, key: str, deleted_by: str = "system") -> bool:
        with self._lock:
            old_value = self.get(key)
            
            keys = key.split(".")
            current = self.config
            
            for k in keys[:-1]:
                if k not in current:
                    return False
                current = current[k]
            
            if keys[-1] in current:
                del current[keys[-1]]
                
                self.history.add(self.config, deleted_by, f"Deleted {key}")
                self.watcher.notify(key, old_value, None)
                return True
            
            return False
    
    def rollback(self, version: int, rolled_back_by: str = "system") -> bool:
        with self._lock:
            old_version = self.history.get_version(version)
            if not old_version:
                return False
            
            old_config = self.config.copy()
            self.config = old_version.config.copy()
            
            for version in self.history.versions:
                if version.version >= old_version.version:
                    version.status = ConfigStatus.DEPRECATED
            
            new_version = self.history.add(
                self.config,
                rolled_back_by,
                f"Rolled back to version {old_version.version}"
            )
            new_version.status = ConfigStatus.ROLLED_BACK
            
            for key in set(list(old_config.keys()) + list(self.config.keys())):
                self.watcher.notify(
                    key,
                    old_config.get(key),
                    self.config.get(key)
                )
            
            return True
    
    def watch(self, key: str, callback: Callable):
        self.watcher.watch(key, callback)
    
    def get_all(self) -> Dict[str, Any]:
        with self._lock:
            return self.config.copy()

class DistributedConfigCenter:
    def __init__(self):
        self.namespaces: Dict[str, ConfigNamespace] = {}
        self._lock = threading.Lock()
    
    def create_namespace(self, name: str) -> ConfigNamespace:
        with self._lock:
            namespace = ConfigNamespace(name)
            self.namespaces[name] = namespace
            return namespace
    
    def get_namespace(self, name: str) -> Optional[ConfigNamespace]:
        return self.namespaces.get(name)
    
    def get(self, namespace: str, key: str, default: Any = None) -> Any:
        ns = self.namespaces.get(namespace)
        if ns:
            return ns.get(key, default)
        return default
    
    def set(self, namespace: str, key: str, value: Any, updated_by: str = "system") -> bool:
        ns = self.namespaces.get(namespace)
        if ns:
            return ns.set(key, value, updated_by)
        return False
    
    def export_all(self) -> Dict[str, Any]:
        return {
            name: ns.get_all()
            for name, ns in self.namespaces.items()
        }
    
    def import_config(self, namespace: str, config: Dict[str, Any], imported_by: str = "system"):
        ns = self.namespaces.get(namespace)
        if not ns:
            ns = self.create_namespace(namespace)
        
        with ns._lock:
            ns.config = config.copy()
            ns.history.add(config, imported_by, "Imported configuration")

def main():
    config_center = DistributedConfigCenter()
    
    app_config = config_center.create_namespace("app")
    db_config = config_center.create_namespace("database")
    
    app_config.set("server.host", "localhost")
    app_config.set("server.port", 8080)
    app_config.set("debug", True)
    
    db_config.set("mysql.host", "localhost")
    db_config.set("mysql.port", 3306)
    db_config.set("mysql.database", "myapp")
    
    print("配置值:")
    print(f"  server.host: {config_center.get('app', 'server.host')}")
    print(f"  server.port: {config_center.get('app', 'server.port')}")
    print(f"  mysql.host: {config_center.get('database', 'mysql.host')}")
    
    changes = []
    
    def on_config_change(key: str, old_value: Any, new_value: Any):
        changes.append(f"{key}: {old_value} -> {new_value}")
    
    app_config.watch("server.port", on_config_change)
    
    print("\n更新配置...")
    app_config.set("server.port", 9090, "admin")
    
    print(f"配置变更: {changes}")
    
    print("\n版本历史:")
    latest = app_config.history.get_latest()
    if latest:
        print(f"  当前版本: {latest.version}")
        print(f"  创建者: {latest.created_by}")
        print(f"  描述: {latest.description}")

if __name__ == "__main__":
    main()
