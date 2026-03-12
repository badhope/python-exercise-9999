# -----------------------------
# 题目：实现简单的分布式存储系统。
# 描述：支持数据分片、复制、一致性。
# -----------------------------

import hashlib
import threading
import time
from collections import defaultdict

class Shard:
    def __init__(self, shard_id):
        self.shard_id = shard_id
        self.data = {}
        self._lock = threading.Lock()
    
    def get(self, key):
        with self._lock:
            return self.data.get(key)
    
    def set(self, key, value):
        with self._lock:
            self.data[key] = value
            return True
    
    def delete(self, key):
        with self._lock:
            return self.data.pop(key, None) is not None
    
    def size(self):
        with self._lock:
            return len(self.data)

class Replica:
    def __init__(self, replica_id, shard):
        self.replica_id = replica_id
        self.shard = shard
        self.last_sync = time.time()
        self.status = "synced"
    
    def sync(self, data):
        with self.shard._lock:
            self.shard.data = data.copy()
        self.last_sync = time.time()
        self.status = "synced"

class ConsistentHash:
    def __init__(self, virtual_nodes=150):
        self.virtual_nodes = virtual_nodes
        self.ring = {}
        self.sorted_keys = []
    
    def _hash(self, key):
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
    
    def add_node(self, node_id):
        for i in range(self.virtual_nodes):
            virtual_key = f"{node_id}#{i}"
            hash_key = self._hash(virtual_key)
            self.ring[hash_key] = node_id
        self.sorted_keys = sorted(self.ring.keys())
    
    def get_node(self, key):
        if not self.ring:
            return None
        hash_key = self._hash(key)
        for k in self.sorted_keys:
            if hash_key <= k:
                return self.ring[k]
        return self.ring[self.sorted_keys[0]]

class DistributedStorage:
    def __init__(self, num_shards=3, replication_factor=2):
        self.num_shards = num_shards
        self.replication_factor = replication_factor
        self.shards = {f"shard-{i}": Shard(i) for i in range(num_shards)}
        self.replicas = defaultdict(list)
        self.hash_ring = ConsistentHash()
        
        for shard_id in self.shards:
            self.hash_ring.add_node(shard_id)
        
        self._setup_replicas()
    
    def _setup_replicas(self):
        shard_ids = list(self.shards.keys())
        for i, shard_id in enumerate(shard_ids):
            for j in range(1, self.replication_factor):
                replica_shard_id = shard_ids[(i + j) % len(shard_ids)]
                replica = Replica(f"{shard_id}-replica-{j}", self.shards[replica_shard_id])
                self.replicas[shard_id].append(replica)
    
    def _get_shard(self, key):
        shard_id = self.hash_ring.get_node(key)
        return self.shards.get(shard_id)
    
    def get(self, key):
        shard = self._get_shard(key)
        if shard:
            return shard.get(key)
        return None
    
    def set(self, key, value):
        shard = self._get_shard(key)
        if shard:
            shard.set(key, value)
            for replica in self.replicas.get(shard.shard_id, []):
                replica.sync(shard.data)
            return True
        return False
    
    def delete(self, key):
        shard = self._get_shard(key)
        if shard:
            return shard.delete(key)
        return False
    
    def get_stats(self):
        return {
            shard_id: shard.size()
            for shard_id, shard in self.shards.items()
        }

def main():
    storage = DistributedStorage(num_shards=3, replication_factor=2)
    
    storage.set("user:1", {"name": "张三", "age": 25})
    storage.set("user:2", {"name": "李四", "age": 30})
    storage.set("product:1", {"name": "笔记本", "price": 5999})
    
    print(f"user:1 -> {storage.get('user:1')}")
    print(f"user:2 -> {storage.get('user:2')}")
    print(f"product:1 -> {storage.get('product:1')}")
    
    print(f"\n分片状态: {storage.get_stats()}")


if __name__ == "__main__":
    main()
