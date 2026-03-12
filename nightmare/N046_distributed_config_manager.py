"""
N046 - 分布式配置管理器
难度：Nightmare

题目描述：
实现一个分布式配置管理系统，支持配置的集中存储、版本管理、动态推送和多环境隔离。
系统需要处理配置变更通知、配置回滚、配置加密等高级功能。

学习目标：
1. 理解分布式配置管理的核心概念
2. 掌握配置版本控制和回滚机制
3. 实现配置变更的实时推送
4. 处理多环境配置隔离

输入输出要求：
输入：配置操作请求（创建、更新、删除、查询、回滚）
输出：操作结果和配置数据

预期解决方案：
使用观察者模式实现配置变更通知，使用版本链实现配置回滚。
"""

import hashlib
import json
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class Environment(Enum):
    DEVELOPMENT = "dev"
    TESTING = "test"
    STAGING = "stage"
    PRODUCTION = "prod"


class ConfigChangeType(Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    ROLLBACK = "rollback"


@dataclass
class ConfigVersion:
    version: int
    key: str
    value: Any
    environment: Environment
    checksum: str
    timestamp: float
    author: str
    comment: str = ""
    encrypted: bool = False
    previous_version: Optional[int] = None


@dataclass
class ConfigChange:
    change_type: ConfigChangeType
    key: str
    old_value: Any
    new_value: Any
    environment: Environment
    version: int
    timestamp: float


class ConfigObserver:
    def __init__(self, name: str):
        self.name = name
        self._callbacks: Dict[str, List[Callable]] = {}
    
    def subscribe(self, key_pattern: str, callback: Callable):
        if key_pattern not in self._callbacks:
            self._callbacks[key_pattern] = []
        self._callbacks[key_pattern].append(callback)
    
    def unsubscribe(self, key_pattern: str, callback: Callable):
        if key_pattern in self._callbacks:
            if callback in self._callbacks[key_pattern]:
                self._callbacks[key_pattern].remove(callback)
    
    def notify(self, change: ConfigChange):
        for pattern, callbacks in self._callbacks.items():
            if self._match_pattern(pattern, change.key):
                for callback in callbacks:
                    try:
                        callback(change)
                    except Exception:
                        pass
    
    def _match_pattern(self, pattern: str, key: str) -> bool:
        if pattern == "*":
            return True
        if pattern.endswith("*"):
            return key.startswith(pattern[:-1])
        return pattern == key


class ConfigEncryption:
    _key = "default_encryption_key_32bytes_long"
    
    @classmethod
    def encrypt(cls, value: str) -> str:
        result = []
        for i, char in enumerate(value):
            key_char = cls._key[i % len(cls._key)]
            encrypted_char = chr(ord(char) ^ ord(key_char))
            result.append(encrypted_char)
        return "".join(result)
    
    @classmethod
    def decrypt(cls, value: str) -> str:
        return cls.encrypt(value)
    
    @classmethod
    def generate_checksum(cls, value: Any) -> str:
        content = json.dumps(value, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()


class ConfigStore:
    def __init__(self):
        self._configs: Dict[str, Dict[Environment, ConfigVersion]] = {}
        self._versions: Dict[str, Dict[Environment, List[ConfigVersion]]] = {}
        self._lock = threading.RLock()
        self._version_counter = 0
    
    def get(self, key: str, env: Environment) -> Optional[ConfigVersion]:
        with self._lock:
            if key in self._configs:
                return self._configs[key].get(env)
        return None
    
    def set(self, key: str, value: Any, env: Environment, 
            author: str, comment: str = "", encrypt: bool = False) -> ConfigVersion:
        with self._lock:
            self._version_counter += 1
            
            previous = self._configs.get(key, {}).get(env)
            previous_version = previous.version if previous else None
            
            actual_value = value
            if encrypt and isinstance(value, str):
                actual_value = ConfigEncryption.encrypt(value)
            
            version = ConfigVersion(
                version=self._version_counter,
                key=key,
                value=actual_value,
                environment=env,
                checksum=ConfigEncryption.generate_checksum(value),
                timestamp=time.time(),
                author=author,
                comment=comment,
                encrypted=encrypt,
                previous_version=previous_version
            )
            
            if key not in self._configs:
                self._configs[key] = {}
            self._configs[key][env] = version
            
            if key not in self._versions:
                self._versions[key] = {}
            if env not in self._versions[key]:
                self._versions[key][env] = []
            self._versions[key][env].append(version)
            
            return version
    
    def delete(self, key: str, env: Environment) -> bool:
        with self._lock:
            if key in self._configs and env in self._configs[key]:
                del self._configs[key][env]
                if not self._configs[key]:
                    del self._configs[key]
                return True
        return False
    
    def get_history(self, key: str, env: Environment) -> List[ConfigVersion]:
        with self._lock:
            if key in self._versions and env in self._versions[key]:
                return list(self._versions[key][env])
        return []
    
    def get_all_keys(self, env: Environment) -> List[str]:
        with self._lock:
            keys = []
            for key, envs in self._configs.items():
                if env in envs:
                    keys.append(key)
            return keys


class DistributedConfigManager:
    def __init__(self):
        self.store = ConfigStore()
        self.observer = ConfigObserver("config_observer")
        self._change_history: List[ConfigChange] = []
        self._lock = threading.Lock()
    
    def create_config(self, key: str, value: Any, env: Environment,
                      author: str, comment: str = "", encrypt: bool = False) -> ConfigVersion:
        existing = self.store.get(key, env)
        if existing:
            raise ValueError(f"Config {key} already exists in {env.value}")
        
        version = self.store.set(key, value, env, author, comment, encrypt)
        
        change = ConfigChange(
            change_type=ConfigChangeType.CREATE,
            key=key,
            old_value=None,
            new_value=value,
            environment=env,
            version=version.version,
            timestamp=time.time()
        )
        
        with self._lock:
            self._change_history.append(change)
        
        self.observer.notify(change)
        
        return version
    
    def update_config(self, key: str, value: Any, env: Environment,
                      author: str, comment: str = "", encrypt: bool = False) -> ConfigVersion:
        existing = self.store.get(key, env)
        if not existing:
            raise ValueError(f"Config {key} not found in {env.value}")
        
        old_value = existing.value
        if existing.encrypted:
            old_value = ConfigEncryption.decrypt(old_value)
        
        version = self.store.set(key, value, env, author, comment, encrypt)
        
        change = ConfigChange(
            change_type=ConfigChangeType.UPDATE,
            key=key,
            old_value=old_value,
            new_value=value,
            environment=env,
            version=version.version,
            timestamp=time.time()
        )
        
        with self._lock:
            self._change_history.append(change)
        
        self.observer.notify(change)
        
        return version
    
    def delete_config(self, key: str, env: Environment) -> bool:
        existing = self.store.get(key, env)
        if not existing:
            return False
        
        old_value = existing.value
        if existing.encrypted:
            old_value = ConfigEncryption.decrypt(old_value)
        
        result = self.store.delete(key, env)
        
        if result:
            change = ConfigChange(
                change_type=ConfigChangeType.DELETE,
                key=key,
                old_value=old_value,
                new_value=None,
                environment=env,
                version=existing.version,
                timestamp=time.time()
            )
            
            with self._lock:
                self._change_history.append(change)
            
            self.observer.notify(change)
        
        return result
    
    def get_config(self, key: str, env: Environment, decrypt: bool = True) -> Optional[Any]:
        version = self.store.get(key, env)
        if not version:
            return None
        
        value = version.value
        if decrypt and version.encrypted and isinstance(value, str):
            value = ConfigEncryption.decrypt(value)
        
        return value
    
    def get_config_metadata(self, key: str, env: Environment) -> Optional[ConfigVersion]:
        return self.store.get(key, env)
    
    def rollback_config(self, key: str, env: Environment, target_version: int,
                        author: str) -> Optional[ConfigVersion]:
        history = self.store.get_history(key, env)
        
        target = None
        for version in history:
            if version.version == target_version:
                target = version
                break
        
        if not target:
            raise ValueError(f"Version {target_version} not found for {key} in {env.value}")
        
        current = self.store.get(key, env)
        old_value = current.value if current else None
        if current and current.encrypted:
            old_value = ConfigEncryption.decrypt(old_value)
        
        new_value = target.value
        if target.encrypted:
            new_value = ConfigEncryption.decrypt(new_value)
        
        new_version = self.store.set(
            key, new_value, env, author,
            f"Rollback to version {target_version}",
            target.encrypted
        )
        
        change = ConfigChange(
            change_type=ConfigChangeType.ROLLBACK,
            key=key,
            old_value=old_value,
            new_value=new_value,
            environment=env,
            version=new_version.version,
            timestamp=time.time()
        )
        
        with self._lock:
            self._change_history.append(change)
        
        self.observer.notify(change)
        
        return new_version
    
    def get_history(self, key: str, env: Environment) -> List[ConfigVersion]:
        return self.store.get_history(key, env)
    
    def get_all_configs(self, env: Environment) -> Dict[str, Any]:
        keys = self.store.get_all_keys(env)
        result = {}
        for key in keys:
            value = self.get_config(key, env)
            if value is not None:
                result[key] = value
        return result
    
    def subscribe(self, key_pattern: str, callback: Callable[[ConfigChange], None]):
        self.observer.subscribe(key_pattern, callback)
    
    def unsubscribe(self, key_pattern: str, callback: Callable[[ConfigChange], None]):
        self.observer.unsubscribe(key_pattern, callback)
    
    def get_change_history(self, limit: int = 100) -> List[ConfigChange]:
        with self._lock:
            return list(self._change_history[-limit:])
    
    def export_configs(self, env: Environment) -> str:
        configs = self.get_all_configs(env)
        export_data = {
            "environment": env.value,
            "timestamp": time.time(),
            "configs": configs
        }
        return json.dumps(export_data, indent=2)
    
    def import_configs(self, data: str, env: Environment, 
                       author: str, overwrite: bool = False) -> int:
        import_data = json.loads(data)
        configs = import_data.get("configs", {})
        
        imported = 0
        for key, value in configs.items():
            existing = self.store.get(key, env)
            if existing and not overwrite:
                continue
            
            if existing:
                self.update_config(key, value, env, author, "Imported")
            else:
                self.create_config(key, value, env, author, "Imported")
            imported += 1
        
        return imported


def main():
    config_manager = DistributedConfigManager()
    
    changes_received = []
    
    def on_config_change(change: ConfigChange):
        changes_received.append(change)
        print(f"配置变更通知: {change.change_type.value} - {change.key}")
    
    config_manager.subscribe("database.*", on_config_change)
    config_manager.subscribe("app.*", on_config_change)
    
    print("=== 创建配置 ===")
    config_manager.create_config(
        "database.host", "localhost", Environment.DEVELOPMENT, 
        "admin", "数据库主机配置"
    )
    config_manager.create_config(
        "database.port", 5432, Environment.DEVELOPMENT,
        "admin", "数据库端口配置"
    )
    config_manager.create_config(
        "database.password", "secret123", Environment.DEVELOPMENT,
        "admin", "数据库密码", encrypt=True
    )
    config_manager.create_config(
        "app.name", "MyApp", Environment.DEVELOPMENT,
        "admin", "应用名称"
    )
    
    print("\n=== 查询配置 ===")
    db_host = config_manager.get_config("database.host", Environment.DEVELOPMENT)
    print(f"database.host: {db_host}")
    
    db_password = config_manager.get_config("database.password", Environment.DEVELOPMENT)
    print(f"database.password (加密): {db_password}")
    
    print("\n=== 更新配置 ===")
    config_manager.update_config(
        "database.host", "192.168.1.100", Environment.DEVELOPMENT,
        "admin", "更新数据库主机地址"
    )
    
    print("\n=== 配置历史 ===")
    history = config_manager.get_history("database.host", Environment.DEVELOPMENT)
    for version in history:
        print(f"版本 {version.version}: {version.value} (by {version.author})")
    
    print("\n=== 配置回滚 ===")
    if len(history) >= 2:
        target_version = history[0].version
        config_manager.rollback_config(
            "database.host", Environment.DEVELOPMENT, target_version, "admin"
        )
        
        current = config_manager.get_config("database.host", Environment.DEVELOPMENT)
        print(f"回滚后: {current}")
    
    print("\n=== 多环境配置 ===")
    config_manager.create_config(
        "database.host", "prod-db.example.com", Environment.PRODUCTION,
        "admin", "生产环境数据库"
    )
    
    dev_configs = config_manager.get_all_configs(Environment.DEVELOPMENT)
    prod_configs = config_manager.get_all_configs(Environment.PRODUCTION)
    
    print(f"开发环境配置数: {len(dev_configs)}")
    print(f"生产环境配置数: {len(prod_configs)}")
    
    print("\n=== 配置导出/导入 ===")
    exported = config_manager.export_configs(Environment.DEVELOPMENT)
    print(f"导出配置: {exported[:200]}...")
    
    imported = config_manager.import_configs(
        exported, Environment.TESTING, "admin"
    )
    print(f"导入配置数: {imported}")
    
    print("\n=== 变更历史 ===")
    changes = config_manager.get_change_history(10)
    for change in changes:
        print(f"{change.timestamp:.2f}: {change.change_type.value} {change.key}")
    
    print(f"\n总共收到 {len(changes_received)} 条配置变更通知")


if __name__ == "__main__":
    main()
