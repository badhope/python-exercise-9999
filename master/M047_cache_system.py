# -----------------------------
# 题目：实现缓存系统。
# 描述：支持多级缓存、缓存策略、过期管理。
# -----------------------------

import time
import threading
import hashlib
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from enum import Enum
from collections import OrderedDict
from functools import wraps

class CacheLevel(Enum):
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"

class EvictionPolicy(Enum):
    LRU = "lru"
    LFU = "lfu"
    FIFO = "fifo"

@dataclass
class CacheEntry:
    key: str
    value: Any
    created_at: float
    expire_at: Optional[float]
    access_count: int = 0
    last_access: float = 0.0
    ttl: float = 300.0

class CacheStore:
    def __init__(
        self,
        name: str,
        max_size: int = 1000,
        default_ttl: float = 300.0,
        eviction_policy: EvictionPolicy = EvictionPolicy.LRU
    ):
        self.name = name
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.eviction_policy = eviction_policy
        self._cache: Dict[str, CacheEntry] = {}
        self._access_order: OrderedDict = OrderedDict()
        self._lock = threading.RLock()
        self._stats = {'hits': 0, 'misses': 0}
    
    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                self._stats['misses'] += 1
                return None
            
            if entry.expire_at and time.time() > entry.expire_at:
                del self._cache[key]
                self._access_order.pop(key, None)
                self._stats['misses'] += 1
                return None
            
            entry.access_count += 1
            entry.last_access = time.time()
            
            if self.eviction_policy == EvictionPolicy.LRU:
                self._access_order.move_to_end(key)
            
            self._stats['hits'] += 1
            return entry.value
    
    def set(self, key: str, value: Any, ttl: float = None) -> bool:
        with self._lock:
            if len(self._cache) >= self.max_size and key not in self._cache:
                self._evict()
            
            now = time.time()
            ttl = ttl or self.default_ttl
            
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=now,
                expire_at=now + ttl if ttl > 0 else None,
                last_access=now,
                ttl=ttl
            )
            
            self._cache[key] = entry
            self._access_order[key] = True
            
            return True
    
    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._access_order.pop(key, None)
                return True
            return False
    
    def exists(self, key: str) -> bool:
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return False
            if entry.expire_at and time.time() > entry.expire_at:
                self.delete(key)
                return False
            return True
    
    def clear(self):
        with self._lock:
            self._cache.clear()
            self._access_order.clear()
    
    def _evict(self):
        if not self._cache:
            return
        
        if self.eviction_policy == EvictionPolicy.LRU:
            key, _ = self._access_order.popitem(last=False)
        elif self.eviction_policy == EvictionPolicy.LFU:
            key = min(self._cache.keys(), key=lambda k: self._cache[k].access_count)
        else:
            key = next(iter(self._cache))
        
        del self._cache[key]
    
    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            total = self._stats['hits'] + self._stats['misses']
            hit_rate = self._stats['hits'] / total if total > 0 else 0
            
            return {
                'name': self.name,
                'size': len(self._cache),
                'max_size': self.max_size,
                'hits': self._stats['hits'],
                'misses': self._stats['misses'],
                'hit_rate': f"{hit_rate:.2%}"
            }

class MultiLevelCache:
    def __init__(self):
        self._levels: Dict[CacheLevel, CacheStore] = {}
        self._lock = threading.Lock()
    
    def add_level(
        self,
        level: CacheLevel,
        max_size: int = 1000,
        default_ttl: float = 300.0,
        eviction_policy: EvictionPolicy = EvictionPolicy.LRU
    ):
        store = CacheStore(
            name=f"cache-{level.value}",
            max_size=max_size,
            default_ttl=default_ttl,
            eviction_policy=eviction_policy
        )
        self._levels[level] = store
    
    def get(self, key: str) -> Optional[Any]:
        for level in [CacheLevel.L1, CacheLevel.L2, CacheLevel.L3]:
            store = self._levels.get(level)
            if store:
                value = store.get(key)
                if value is not None:
                    self._promote(key, value, level)
                    return value
        return None
    
    def _promote(self, key: str, value: Any, from_level: CacheLevel):
        levels = [CacheLevel.L1, CacheLevel.L2, CacheLevel.L3]
        from_index = levels.index(from_level)
        
        for i in range(from_index):
            store = self._levels.get(levels[i])
            if store:
                store.set(key, value)
    
    def set(self, key: str, value: Any, ttl: float = None):
        for store in self._levels.values():
            store.set(key, value, ttl)
    
    def delete(self, key: str):
        for store in self._levels.values():
            store.delete(key)
    
    def clear(self):
        for store in self._levels.values():
            store.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            level.value: store.get_stats()
            for level, store in self._levels.items()
        }

class CacheManager:
    def __init__(self):
        self._caches: Dict[str, CacheStore] = {}
        self._multi_level_cache: Optional[MultiLevelCache] = None
    
    def create_cache(
        self,
        name: str,
        max_size: int = 1000,
        default_ttl: float = 300.0,
        eviction_policy: EvictionPolicy = EvictionPolicy.LRU
    ) -> CacheStore:
        cache = CacheStore(name, max_size, default_ttl, eviction_policy)
        self._caches[name] = cache
        return cache
    
    def get_cache(self, name: str) -> Optional[CacheStore]:
        return self._caches.get(name)
    
    def setup_multi_level(self, l1_size: int = 100, l2_size: int = 1000, l3_size: int = 10000):
        self._multi_level_cache = MultiLevelCache()
        self._multi_level_cache.add_level(CacheLevel.L1, max_size=l1_size, default_ttl=60)
        self._multi_level_cache.add_level(CacheLevel.L2, max_size=l2_size, default_ttl=300)
        self._multi_level_cache.add_level(CacheLevel.L3, max_size=l3_size, default_ttl=1800)
    
    def get_multi_level(self) -> Optional[MultiLevelCache]:
        return self._multi_level_cache
    
    def get_all_stats(self) -> Dict[str, Any]:
        return {
            name: cache.get_stats()
            for name, cache in self._caches.items()
        }

def cached(cache: CacheStore, key_func: Callable = None, ttl: float = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator

def main():
    manager = CacheManager()
    
    user_cache = manager.create_cache("users", max_size=100, default_ttl=60)
    product_cache = manager.create_cache("products", max_size=500, default_ttl=300)
    
    user_cache.set("user:1", {"id": 1, "name": "张三"})
    user_cache.set("user:2", {"id": 2, "name": "李四"})
    
    print(f"用户1: {user_cache.get('user:1')}")
    print(f"用户3: {user_cache.get('user:3')}")
    
    print(f"\n缓存统计:")
    for name, stats in manager.get_all_stats().items():
        print(f"  {name}: 命中率 {stats['hit_rate']}, 大小 {stats['size']}/{stats['max_size']}")
    
    manager.setup_multi_level()
    mlc = manager.get_multi_level()
    
    mlc.set("data:1", {"value": "重要数据"})
    
    print(f"\n多级缓存获取: {mlc.get('data:1')}")
    print(f"多级缓存统计: {mlc.get_stats()}")

if __name__ == "__main__":
    main()
