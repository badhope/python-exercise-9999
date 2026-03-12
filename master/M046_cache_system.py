# -----------------------------
# 题目：实现缓存系统。
# -----------------------------

import time
import threading
from collections import OrderedDict

class Cache:
    def __init__(self, max_size=1000, ttl=3600):
        self.max_size = max_size
        self.ttl = ttl
        self.cache = OrderedDict()
        self.timestamps = {}
        self.lock = threading.Lock()
    
    def get(self, key):
        with self.lock:
            if key not in self.cache:
                return None
            
            if self._is_expired(key):
                del self.cache[key]
                del self.timestamps[key]
                return None
            
            self.cache.move_to_end(key)
            return self.cache[key]
    
    def set(self, key, value):
        with self.lock:
            if key in self.cache:
                del self.cache[key]
            elif len(self.cache) >= self.max_size:
                oldest = next(iter(self.cache))
                del self.cache[oldest]
                del self.timestamps[oldest]
            
            self.cache[key] = value
            self.timestamps[key] = time.time()
    
    def delete(self, key):
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                del self.timestamps[key]
                return True
            return False
    
    def clear(self):
        with self.lock:
            self.cache.clear()
            self.timestamps.clear()
    
    def _is_expired(self, key):
        if key not in self.timestamps:
            return True
        return time.time() - self.timestamps[key] > self.ttl

if __name__ == "__main__":
    cache = Cache(max_size=3, ttl=2)
    
    cache.set("a", 1)
    cache.set("b", 2)
    cache.set("c", 3)
    
    print(f"Get a: {cache.get('a')}")
    
    cache.set("d", 4)
    print(f"Get a after eviction: {cache.get('a')}")
    
    time.sleep(3)
    print(f"Get b after TTL: {cache.get('b')}")
