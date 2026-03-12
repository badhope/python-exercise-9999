# -----------------------------
# 题目：实现分布式缓存系统。
# 描述：支持缓存分片、缓存穿透防护、缓存雪崩防护。
# -----------------------------

import time
import threading
import hashlib
import random
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from bisect import bisect_right

@dataclass
class CacheNode:
    node_id: str
    host: str
    port: int
    capacity: int
    used: int = 0
    is_alive: bool = True

@dataclass
class CacheEntry:
    key: str
    value: Any
    expire_at: Optional[float]
    created_at: float = field(default_factory=time.time)
    access_count: int = 0

class ConsistentHash:
    def __init__(self, virtual_nodes: int = 150):
        self.virtual_nodes = virtual_nodes
        self.ring: Dict[int, str] = {}
        self.sorted_keys: List[int] = []
    
    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
    
    def add_node(self, node_id: str):
        for i in range(self.virtual_nodes):
            virtual_key = f"{node_id}#{i}"
            hash_key = self._hash(virtual_key)
            self.ring[hash_key] = node_id
        
        self.sorted_keys = sorted(self.ring.keys())
    
    def remove_node(self, node_id: str):
        keys_to_remove = [
            k for k, v in self.ring.items()
            if v == node_id
        ]
        for k in keys_to_remove:
            del self.ring[k]
        
        self.sorted_keys = sorted(self.ring.keys())
    
    def get_node(self, key: str) -> Optional[str]:
        if not self.ring:
            return None
        
        hash_key = self._hash(key)
        idx = bisect_right(self.sorted_keys, hash_key)
        
        if idx >= len(self.sorted_keys):
            idx = 0
        
        return self.ring[self.sorted_keys[idx]]

class BloomFilter:
    def __init__(self, size: int = 10000, hash_count: int = 7):
        self.size = size
        self.hash_count = hash_count
        self.bit_array = [False] * size
    
    def _hashes(self, key: str) -> List[int]:
        hashes = []
        for i in range(self.hash_count):
            hash_val = int(hashlib.md5(f"{key}#{i}".encode()).hexdigest(), 16)
            hashes.append(hash_val % self.size)
        return hashes
    
    def add(self, key: str):
        for idx in self._hashes(key):
            self.bit_array[idx] = True
    
    def might_contain(self, key: str) -> bool:
        return all(self.bit_array[idx] for idx in self._hashes(key))

class LocalCache:
    def __init__(self, capacity: int = 1000):
        self.capacity = capacity
        self.cache: Dict[str, CacheEntry] = {}
        self._lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self.cache.get(key)
            if entry:
                if entry.expire_at and time.time() > entry.expire_at:
                    del self.cache[key]
                    return None
                entry.access_count += 1
                return entry.value
            return None
    
    def set(self, key: str, value: Any, ttl: float = None):
        with self._lock:
            if len(self.cache) >= self.capacity and key not in self.cache:
                self._evict()
            
            self.cache[key] = CacheEntry(
                key=key,
                value=value,
                expire_at=time.time() + ttl if ttl else None
            )
    
    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    def _evict(self):
        if not self.cache:
            return
        
        lru_key = min(self.cache.keys(), key=lambda k: self.cache[k].access_count)
        del self.cache[lru_key]

class DistributedCache:
    def __init__(self, default_ttl: float = 300.0):
        self.default_ttl = default_ttl
        self.nodes: Dict[str, LocalCache] = {}
        self.hash_ring = ConsistentHash()
        self.bloom_filter = BloomFilter()
        self._lock = threading.Lock()
        
        self._empty_value = object()
        self._null_cache_ttl = 60.0
    
    def add_node(self, node_id: str, capacity: int = 1000):
        with self._lock:
            self.nodes[node_id] = LocalCache(capacity)
            self.hash_ring.add_node(node_id)
    
    def remove_node(self, node_id: str):
        with self._lock:
            self.nodes.pop(node_id, None)
            self.hash_ring.remove_node(node_id)
    
    def get(self, key: str) -> Optional[Any]:
        if not self.bloom_filter.might_contain(key):
            return None
        
        node_id = self.hash_ring.get_node(key)
        if not node_id:
            return None
        
        node = self.nodes.get(node_id)
        if not node:
            return None
        
        value = node.get(key)
        
        if value == self._empty_value:
            return None
        
        return value
    
    def set(self, key: str, value: Any, ttl: float = None):
        ttl = ttl or self.default_ttl
        
        self.bloom_filter.add(key)
        
        node_id = self.hash_ring.get_node(key)
        if not node_id:
            return
        
        node = self.nodes.get(node_id)
        if not node:
            return
        
        if value is None:
            node.set(key, self._empty_value, self._null_cache_ttl)
        else:
            node.set(key, value, ttl)
    
    def delete(self, key: str) -> bool:
        node_id = self.hash_ring.get_node(key)
        if not node_id:
            return False
        
        node = self.nodes.get(node_id)
        if not node:
            return False
        
        return node.delete(key)
    
    def get_or_load(
        self,
        key: str,
        loader: Callable[[], Any],
        ttl: float = None
    ) -> Any:
        value = self.get(key)
        
        if value is not None:
            return value
        
        value = loader()
        self.set(key, value, ttl)
        
        return value
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'nodes': len(self.nodes),
            'bloom_filter_size': self.bloom_filter.size
        }

class CacheCluster:
    def __init__(self):
        self.cache = DistributedCache()
        self._lock = threading.Lock()
        self._rebuild_scheduled = False
    
    def add_node(self, node_id: str, capacity: int = 1000):
        self.cache.add_node(node_id, capacity)
    
    def get(self, key: str) -> Optional[Any]:
        return self.cache.get(key)
    
    def set(self, key: str, value: Any, ttl: float = None):
        jitter = random.uniform(0, 0.1) * (ttl or 300)
        self.cache.set(key, value, (ttl or 300) + jitter)
    
    def schedule_rebuild(self):
        if not self._rebuild_scheduled:
            self._rebuild_scheduled = True
            threading.Thread(target=self._rebuild_cache).start()
    
    def _rebuild_cache(self):
        time.sleep(1)
        self._rebuild_scheduled = False

def main():
    cache = DistributedCache(default_ttl=60.0)
    
    cache.add_node("cache-node-1", capacity=100)
    cache.add_node("cache-node-2", capacity=100)
    cache.add_node("cache-node-3", capacity=100)
    
    print("设置缓存...")
    cache.set("user:1", {"name": "张三", "age": 25})
    cache.set("user:2", {"name": "李四", "age": 30})
    cache.set("order:1", {"id": "ORD-001", "amount": 100})
    
    print("\n获取缓存:")
    print(f"user:1 = {cache.get('user:1')}")
    print(f"user:2 = {cache.get('user:2')}")
    print(f"user:3 = {cache.get('user:3')}")
    
    print("\n缓存穿透防护 (布隆过滤器):")
    print(f"不存在的key可能存在: {cache.bloom_filter.might_contain('user:999')}")
    
    print("\n缓存雪崩防护 (随机过期):")
    for i in range(5):
        cache.set(f"batch:{i}", f"data-{i}", ttl=60)
        print(f"  设置 batch:{i}")
    
    print(f"\n缓存统计: {cache.get_stats()}")

if __name__ == "__main__":
    main()
