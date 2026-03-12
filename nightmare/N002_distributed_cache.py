# -----------------------------
# 题目：实现简单的分布式缓存。
# 描述：支持缓存分片、失效、一致性。
# -----------------------------

import hashlib
import time
import threading
from collections import defaultdict

class CacheNode:
    def __init__(self, node_id):
        self.node_id = node_id
        self.cache = {}
        self._lock = threading.Lock()
    
    def get(self, key):
        with self._lock:
            item = self.cache.get(key)
            if item:
                value, expire_at = item
                if expire_at is None or time.time() < expire_at:
                    return value
                del self.cache[key]
            return None
    
    def set(self, key, value, ttl=None):
        with self._lock:
            expire_at = time.time() + ttl if ttl else None
            self.cache[key] = (value, expire_at)
    
    def delete(self, key):
        with self._lock:
            self.cache.pop(key, None)
    
    def clear(self):
        with self._lock:
            self.cache.clear()

class ConsistentHashing:
    def __init__(self, virtual_nodes=150):
        self.virtual_nodes = virtual_nodes
        self.ring = {}
        self.sorted_keys = []
    
    def _hash(self, key):
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
    
    def add_node(self, node):
        for i in range(self.virtual_nodes):
            virtual_key = f"{node.node_id}#{i}"
            hash_key = self._hash(virtual_key)
            self.ring[hash_key] = node
        self.sorted_keys = sorted(self.ring.keys())
    
    def remove_node(self, node_id):
        for i in range(self.virtual_nodes):
            virtual_key = f"{node_id}#{i}"
            hash_key = self._hash(virtual_key)
            self.ring.pop(hash_key, None)
        self.sorted_keys = sorted(self.ring.keys())
    
    def get_node(self, key):
        if not self.ring:
            return None
        hash_key = self._hash(key)
        for k in self.sorted_keys:
            if hash_key <= k:
                return self.ring[k]
        return self.ring[self.sorted_keys[0]]

class DistributedCache:
    def __init__(self, num_nodes=3):
        self.nodes = [CacheNode(f"node_{i}") for i in range(num_nodes)]
        self.hash_ring = ConsistentHashing()
        for node in self.nodes:
            self.hash_ring.add_node(node)
    
    def get(self, key):
        node = self.hash_ring.get_node(key)
        if node:
            return node.get(key)
        return None
    
    def set(self, key, value, ttl=None):
        node = self.hash_ring.get_node(key)
        if node:
            node.set(key, value, ttl)
    
    def delete(self, key):
        node = self.hash_ring.get_node(key)
        if node:
            node.delete(key)

def main():
    cache = DistributedCache(3)
    
    cache.set("user:1", {"name": "张三"}, ttl=60)
    cache.set("user:2", {"name": "李四"}, ttl=60)
    
    print(f"user:1 -> {cache.get('user:1')}")
    print(f"user:2 -> {cache.get('user:2')}")


if __name__ == "__main__":
    main()
