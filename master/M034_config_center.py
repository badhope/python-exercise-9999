# -----------------------------
# 题目：实现配置中心。
# 描述：支持配置管理、热更新、版本控制。
# -----------------------------

import json
import time
import threading
import hashlib
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from copy import deepcopy

@dataclass
class ConfigEntry:
    key: str
    value: Any
    version: int
    updated_at: float
    updated_by: str = "system"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConfigSnapshot:
    version: int
    timestamp: float
    config: Dict[str, Any]
    checksum: str

class ConfigStore:
    def __init__(self):
        self._configs: Dict[str, ConfigEntry] = {}
        self._snapshots: List[ConfigSnapshot] = []
        self._version = 0
        self._lock = threading.RLock()
        self._max_snapshots = 100
    
    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            entry = self._configs.get(key)
            return entry.value if entry else default
    
    def set(self, key: str, value: Any, updated_by: str = "system", metadata: dict = None):
        with self._lock:
            self._version += 1
            
            self._configs[key] = ConfigEntry(
                key=key,
                value=value,
                version=self._version,
                updated_at=time.time(),
                updated_by=updated_by,
                metadata=metadata or {}
            )
            
            self._create_snapshot()
    
    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._configs:
                del self._configs[key]
                self._version += 1
                self._create_snapshot()
                return True
            return False
    
    def get_all(self) -> Dict[str, Any]:
        with self._lock:
            return {k: v.value for k, v in self._configs.items()}
    
    def get_entry(self, key: str) -> Optional[ConfigEntry]:
        with self._lock:
            return self._configs.get(key)
    
    def _create_snapshot(self):
        config = self.get_all()
        checksum = self._calculate_checksum(config)
        
        snapshot = ConfigSnapshot(
            version=self._version,
            timestamp=time.time(),
            config=deepcopy(config),
            checksum=checksum
        )
        
        self._snapshots.append(snapshot)
        
        if len(self._snapshots) > self._max_snapshots:
            self._snapshots.pop(0)
    
    def _calculate_checksum(self, config: Dict[str, Any]) -> str:
        data = json.dumps(config, sort_keys=True)
        return hashlib.md5(data.encode()).hexdigest()
    
    def get_snapshot(self, version: int = None) -> Optional[ConfigSnapshot]:
        with self._lock:
            if version is None:
                return self._snapshots[-1] if self._snapshots else None
            
            for snapshot in self._snapshots:
                if snapshot.version == version:
                    return snapshot
            return None
    
    def list_snapshots(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [
                {
                    'version': s.version,
                    'timestamp': s.timestamp,
                    'checksum': s.checksum
                }
                for s in self._snapshots
            ]
    
    def rollback(self, version: int) -> bool:
        snapshot = self.get_snapshot(version)
        if not snapshot:
            return False
        
        with self._lock:
            self._configs.clear()
            
            for key, value in snapshot.config.items():
                self._configs[key] = ConfigEntry(
                    key=key,
                    value=value,
                    version=self._version,
                    updated_at=time.time(),
                    updated_by="rollback"
                )
            
            self._version += 1
            self._create_snapshot()
        
        return True

class ConfigWatcher:
    def __init__(self, store: ConfigStore):
        self._store = store
        self._watchers: Dict[str, List[Callable]] = {}
        self._watcher_thread: Optional[threading.Thread] = None
        self._running = False
        self._last_checksum = ""
    
    def watch(self, key: str, callback: Callable[[str, Any], None]):
        if key not in self._watchers:
            self._watchers[key] = []
        self._watchers[key].append(callback)
    
    def watch_all(self, callback: Callable[[Dict[str, Any]], None]):
        if '*' not in self._watchers:
            self._watchers['*'] = []
        self._watchers['*'].append(callback)
    
    def start(self, interval: float = 1.0):
        self._running = True
        self._watcher_thread = threading.Thread(
            target=self._watch_loop,
            args=(interval,)
        )
        self._watcher_thread.daemon = True
        self._watcher_thread.start()
    
    def stop(self):
        self._running = False
        if self._watcher_thread:
            self._watcher_thread.join(timeout=2.0)
    
    def _watch_loop(self, interval: float):
        while self._running:
            snapshot = self._store.get_snapshot()
            if snapshot and snapshot.checksum != self._last_checksum:
                self._last_checksum = snapshot.checksum
                self._notify_watchers(snapshot.config)
            
            time.sleep(interval)
    
    def _notify_watchers(self, config: Dict[str, Any]):
        for key, callbacks in self._watchers.items():
            if key == '*':
                for callback in callbacks:
                    try:
                        callback(config)
                    except Exception:
                        pass
            elif key in config:
                for callback in callbacks:
                    try:
                        callback(key, config[key])
                    except Exception:
                        pass

class ConfigCenter:
    def __init__(self):
        self.store = ConfigStore()
        self.watcher = ConfigWatcher(self.store)
        self._namespaces: Dict[str, ConfigStore] = {}
    
    def get(self, key: str, default: Any = None, namespace: str = None) -> Any:
        if namespace:
            store = self._namespaces.get(namespace)
            return store.get(key, default) if store else default
        return self.store.get(key, default)
    
    def set(self, key: str, value: Any, namespace: str = None, **kwargs):
        if namespace:
            if namespace not in self._namespaces:
                self._namespaces[namespace] = ConfigStore()
            self._namespaces[namespace].set(key, value, **kwargs)
        else:
            self.store.set(key, value, **kwargs)
    
    def get_namespace(self, namespace: str) -> Dict[str, Any]:
        store = self._namespaces.get(namespace)
        return store.get_all() if store else {}
    
    def list_namespaces(self) -> List[str]:
        return list(self._namespaces.keys())
    
    def watch(self, key: str, callback: Callable, namespace: str = None):
        if namespace:
            store = self._namespaces.get(namespace)
            if store:
                watcher = ConfigWatcher(store)
                watcher.watch(key, callback)
                watcher.start()
        else:
            self.watcher.watch(key, callback)
    
    def start_watcher(self):
        self.watcher.start()
    
    def stop_watcher(self):
        self.watcher.stop()
    
    def export_config(self, namespace: str = None) -> str:
        if namespace:
            config = self.get_namespace(namespace)
        else:
            config = self.store.get_all()
        return json.dumps(config, indent=2, ensure_ascii=False)
    
    def import_config(self, config_str: str, namespace: str = None, merge: bool = True):
        config = json.loads(config_str)
        
        if not merge:
            if namespace:
                if namespace in self._namespaces:
                    self._namespaces[namespace]._configs.clear()
            else:
                self.store._configs.clear()
        
        for key, value in config.items():
            self.set(key, value, namespace)
    
    def get_history(self, namespace: str = None) -> List[Dict[str, Any]]:
        if namespace:
            store = self._namespaces.get(namespace)
            return store.list_snapshots() if store else []
        return self.store.list_snapshots()

def main():
    config = ConfigCenter()
    
    config.set("database.host", "localhost")
    config.set("database.port", 3306)
    config.set("database.name", "myapp")
    config.set("cache.enabled", True)
    
    config.set("api.key", "secret123", namespace="production")
    config.set("api.url", "https://api.example.com", namespace="production")
    
    print(f"数据库主机: {config.get('database.host')}")
    print(f"数据库端口: {config.get('database.port')}")
    
    print(f"\n生产环境API: {config.get('api.url', namespace='production')}")
    
    print(f"\n命名空间列表: {config.list_namespaces()}")
    
    print(f"\n配置历史: {config.get_history()}")
    
    exported = config.export_config()
    print(f"\n导出配置:\n{exported}")

if __name__ == "__main__":
    main()
