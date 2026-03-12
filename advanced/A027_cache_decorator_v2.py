# -----------------------------
# 题目：实现简单的缓存装饰器。
# -----------------------------

import time
import functools
import hashlib
import pickle
from typing import Callable, Any, Dict, Optional

class CacheEntry:
    def __init__(self, value: Any, ttl: int):
        self.value = value
        self.expires_at = time.time() + ttl if ttl > 0 else float('inf')
    
    def is_expired(self) -> bool:
        return time.time() > self.expires_at

class MemoryCache:
    def __init__(self, max_size: int = 1000):
        self._cache: Dict[str, CacheEntry] = {}
        self._max_size = max_size
        self._hits = 0
        self._misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            entry = self._cache[key]
            if not entry.is_expired():
                self._hits += 1
                return entry.value
            else:
                del self._cache[key]
        self._misses += 1
        return None
    
    def set(self, key: str, value: Any, ttl: int = 300):
        if len(self._cache) >= self._max_size:
            self._evict_expired()
            if len(self._cache) >= self._max_size:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
        
        self._cache[key] = CacheEntry(value, ttl)
    
    def delete(self, key: str) -> bool:
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self):
        self._cache.clear()
    
    def _evict_expired(self):
        expired_keys = [k for k, v in self._cache.items() if v.is_expired()]
        for key in expired_keys:
            del self._cache[key]
    
    def get_stats(self) -> Dict:
        total = self._hits + self._misses
        hit_rate = self._hits / total * 100 if total > 0 else 0
        return {
            'size': len(self._cache),
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate': f"{hit_rate:.2f}%"
        }

def cached(ttl: int = 300, key_prefix: str = ''):
    cache = MemoryCache()
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = _generate_key(key_prefix, func.__name__, args, kwargs)
            
            result = cache.get(key)
            if result is not None:
                return result
            
            result = func(*args, **kwargs)
            cache.set(key, result, ttl)
            
            return result
        
        wrapper.cache = cache
        wrapper.cache_clear = cache.clear
        wrapper.cache_stats = cache.get_stats
        
        return wrapper
    
    return decorator

def _generate_key(prefix: str, func_name: str, args: tuple, kwargs: dict) -> str:
    key_data = f"{prefix}:{func_name}:{args}:{sorted(kwargs.items())}"
    return hashlib.md5(key_data.encode()).hexdigest()

class CacheManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._caches: Dict[str, MemoryCache] = {}
        return cls._instance
    
    def get_cache(self, name: str = 'default') -> MemoryCache:
        if name not in self._caches:
            self._caches[name] = MemoryCache()
        return self._caches[name]
    
    def clear_all(self):
        for cache in self._caches.values():
            cache.clear()

def cached_method(ttl: int = 300):
    def decorator(func: Callable) -> Callable:
        cache_attr = f'_cache_{func.__name__}'
        
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if not hasattr(self, cache_attr):
                setattr(self, cache_attr, MemoryCache())
            
            cache = getattr(self, cache_attr)
            key = _generate_key('', func.__name__, args, kwargs)
            
            result = cache.get(key)
            if result is not None:
                return result
            
            result = func(self, *args, **kwargs)
            cache.set(key, result, ttl)
            
            return result
        
        return wrapper
    
    return decorator

def main():
    @cached(ttl=60, key_prefix='fib')
    def fibonacci(n: int) -> int:
        if n <= 1:
            return n
        return fibonacci(n - 1) + fibonacci(n - 2)
    
    print("=== 缓存装饰器测试 ===")
    
    start = time.time()
    result1 = fibonacci(30)
    time1 = time.time() - start
    print(f"第一次计算 fib(30) = {result1}, 耗时: {time1:.4f}秒")
    
    start = time.time()
    result2 = fibonacci(30)
    time2 = time.time() - start
    print(f"第二次计算 fib(30) = {result2}, 耗时: {time2:.4f}秒")
    
    print(f"\n缓存统计: {fibonacci.cache_stats()}")
    
    print("\n=== 方法缓存测试 ===")
    class DataService:
        def __init__(self):
            self.call_count = 0
        
        @cached_method(ttl=10)
        def get_data(self, key: str):
            self.call_count += 1
            return f"数据_{key}_{self.call_count}"
    
    service = DataService()
    print(service.get_data("test"))
    print(service.get_data("test"))
    print(service.get_data("other"))


if __name__ == "__main__":
    main()
