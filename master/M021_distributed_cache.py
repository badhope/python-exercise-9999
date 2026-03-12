# -----------------------------
# 题目：实现分布式缓存。
# 描述：支持缓存穿透、击穿、雪崩防护。
# -----------------------------

import time
import threading
import hashlib
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
from collections import OrderedDict
from functools import wraps

@dataclass
class CacheEntry:
    value: Any
    expire_at: float
    created_at: float
    access_count: int = 0
    last_access: float = 0.0

class LocalCache:
    def __init__(self, max_size: int = 1000, default_ttl: float = 300.0):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        self._stats = {'hits': 0, 'misses': 0}
    
    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self.cache.get(key)
            if entry is None:
                self._stats['misses'] += 1
                return None
            
            if time.time() > entry.expire_at:
                del self.cache[key]
                self._stats['misses'] += 1
                return None
            
            entry.access_count += 1
            entry.last_access = time.time()
            self._stats['hits'] += 1
            return entry.value
    
    def set(self, key: str, value: Any, ttl: float = None) -> bool:
        with self._lock:
            if len(self.cache) >= self.max_size and key not in self.cache:
                self._evict()
            
            now = time.time()
            self.cache[key] = CacheEntry(
                value=value,
                expire_at=now + (ttl or self.default_ttl),
                created_at=now,
                last_access=now
            )
            return True
    
    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    def _evict(self):
        if not self.cache:
            return
        
        oldest_key = min(
            self.cache.keys(),
            key=lambda k: self.cache[k].last_access
        )
        del self.cache[oldest_key]
    
    def clear_expired(self) -> int:
        with self._lock:
            now = time.time()
            expired_keys = [
                k for k, v in self.cache.items()
                if now > v.expire_at
            ]
            for key in expired_keys:
                del self.cache[key]
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            total = self._stats['hits'] + self._stats['misses']
            hit_rate = self._stats['hits'] / total if total > 0 else 0
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hits': self._stats['hits'],
                'misses': self._stats['misses'],
                'hit_rate': hit_rate
            }

class BloomFilter:
    def __init__(self, size: int = 10000, hash_count: int = 7):
        self.size = size
        self.hash_count = hash_count
        self.bit_array = [False] * size
    
    def _hashes(self, key: str) -> List[int]:
        hashes = []
        for i in range(self.hash_count):
            h = hashlib.md5(f"{key}:{i}".encode()).hexdigest()
            hashes.append(int(h, 16) % self.size)
        return hashes
    
    def add(self, key: str):
        for index in self._hashes(key):
            self.bit_array[index] = True
    
    def might_contain(self, key: str) -> bool:
        return all(self.bit_array[i] for i in self._hashes(key))

class DistributedCache:
    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: float = 300.0,
        enable_bloom_filter: bool = True
    ):
        self.local_cache = LocalCache(max_size, default_ttl)
        self.bloom_filter = BloomFilter() if enable_bloom_filter else None
        self._lock = threading.Lock()
        self._refresh_locks: Dict[str, threading.Lock] = {}
    
    def get(
        self,
        key: str,
        loader: Callable[[], Any] = None,
        ttl: float = None
    ) -> Optional[Any]:
        value = self.local_cache.get(key)
        if value is not None:
            return value
        
        if self.bloom_filter and not self.bloom_filter.might_contain(key):
            return None
        
        if loader:
            return self._load_and_cache(key, loader, ttl)
        
        return None
    
    def _load_and_cache(
        self,
        key: str,
        loader: Callable[[], Any],
        ttl: float = None
    ) -> Optional[Any]:
        if key not in self._refresh_locks:
            with self._lock:
                if key not in self._refresh_locks:
                    self._refresh_locks[key] = threading.Lock()
        
        with self._refresh_locks[key]:
            value = self.local_cache.get(key)
            if value is not None:
                return value
            
            try:
                value = loader()
                if value is not None:
                    self.set(key, value, ttl)
                return value
            except Exception:
                return None
    
    def set(self, key: str, value: Any, ttl: float = None):
        self.local_cache.set(key, value, ttl)
        if self.bloom_filter:
            self.bloom_filter.add(key)
    
    def delete(self, key: str) -> bool:
        return self.local_cache.delete(key)
    
    def get_or_set(
        self,
        key: str,
        loader: Callable[[], Any],
        ttl: float = None
    ) -> Any:
        value = self.get(key)
        if value is not None:
            return value
        
        value = loader()
        if value is not None:
            self.set(key, value, ttl)
        return value
    
    def invalidate_pattern(self, pattern: str) -> int:
        count = 0
        with self.local_cache._lock:
            keys_to_delete = [
                k for k in self.local_cache.cache.keys()
                if pattern in k
            ]
            for key in keys_to_delete:
                del self.local_cache.cache[key]
                count += 1
        return count
    
    def get_stats(self) -> Dict[str, Any]:
        return self.local_cache.get_stats()

def cache_result(ttl: float = 300.0, key_prefix: str = ""):
    _cache = LocalCache()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"
            
            result = _cache.get(cache_key)
            if result is not None:
                return result
            
            result = func(*args, **kwargs)
            _cache.set(cache_key, result, ttl)
            return result
        
        wrapper.cache_clear = lambda: _cache.cache.clear()
        wrapper.cache_stats = lambda: _cache.get_stats()
        
        return wrapper
    
    return decorator

def main():
    cache = DistributedCache(max_size=100, default_ttl=60.0)
    
    cache.set("user:1", {"id": 1, "name": "张三"})
    cache.set("user:2", {"id": 2, "name": "李四"})
    
    print(f"获取user:1: {cache.get('user:1')}")
    print(f"获取user:3: {cache.get('user:3')}")
    
    def load_user():
        print("从数据库加载用户...")
        return {"id": 3, "name": "王五"}
    
    user3 = cache.get("user:3", loader=load_user)
    print(f"通过loader获取: {user3}")
    
    @cache_result(ttl=30.0, key_prefix="calc")
    def expensive_calculation(n: int) -> int:
        print(f"计算 {n} 的平方...")
        return n * n
    
    print(f"第一次计算: {expensive_calculation(5)}")
    print(f"第二次计算(缓存): {expensive_calculation(5)}")
    
    print(f"\n缓存统计: {cache.get_stats()}")

if __name__ == "__main__":
    main()
