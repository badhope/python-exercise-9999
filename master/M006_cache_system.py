# -----------------------------
# 题目：实现简单的缓存系统。
# 描述：支持内存缓存、文件缓存、过期时间。
# -----------------------------

import time
import pickle
import os
from functools import wraps

class CacheBackend:
    def get(self, key):
        raise NotImplementedError
    
    def set(self, key, value, ttl=None):
        raise NotImplementedError
    
    def delete(self, key):
        raise NotImplementedError

class MemoryCache(CacheBackend):
    def __init__(self):
        self.cache = {}
    
    def get(self, key):
        if key in self.cache:
            value, expire_at = self.cache[key]
            if expire_at is None or time.time() < expire_at:
                return value
            del self.cache[key]
        return None
    
    def set(self, key, value, ttl=None):
        expire_at = time.time() + ttl if ttl else None
        self.cache[key] = (value, expire_at)
    
    def delete(self, key):
        if key in self.cache:
            del self.cache[key]

class FileCache(CacheBackend):
    def __init__(self, cache_dir='.cache'):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_path(self, key):
        return os.path.join(self.cache_dir, f"{key}.cache")
    
    def get(self, key):
        path = self._get_path(key)
        if os.path.exists(path):
            with open(path, 'rb') as f:
                value, expire_at = pickle.load(f)
                if expire_at is None or time.time() < expire_at:
                    return value
                os.remove(path)
        return None
    
    def set(self, key, value, ttl=None):
        expire_at = time.time() + ttl if ttl else None
        with open(self._get_path(key), 'wb') as f:
            pickle.dump((value, expire_at), f)
    
    def delete(self, key):
        path = self._get_path(key)
        if os.path.exists(path):
            os.remove(path)

def cached(cache_backend, key=None, ttl=300):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = key or f"{func.__name__}:{args}:{kwargs}"
            result = cache_backend.get(cache_key)
            if result is not None:
                return result
            result = func(*args, **kwargs)
            cache_backend.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator

def main():
    cache = MemoryCache()
    
    @cached(cache, ttl=60)
    def expensive_operation(n):
        print(f"计算 {n} 的平方...")
        return n ** 2
    
    print(expensive_operation(5))
    print(expensive_operation(5))


if __name__ == "__main__":
    main()
