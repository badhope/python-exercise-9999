# -----------------------------
# 题目：实现分布式键值存储。
# 描述：支持数据分片、副本复制、一致性哈希。
# -----------------------------

import hashlib
import time
import threading
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from bisect import bisect_right

@dataclass
class Node:
    node_id: str
    host: str
    port: int
    virtual_nodes: int = 150
    is_alive: bool = True

@dataclass
class ReplicaSet:
    key: str
    value: Any
    version: int
    replicas: Set[str] = field(default_factory=set)

class ConsistentHash:
    def __init__(self, virtual_nodes: int = 150):
        self.virtual_nodes = virtual_nodes
        self.ring: Dict[int, str] = {}
        self.sorted_keys: List[int] = []
        self._lock = threading.Lock()
    
    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
    
    def add_node(self, node: Node):
        with self._lock:
            for i in range(node.virtual_nodes):
                virtual_key = f"{node.node_id}#{i}"
                hash_key = self._hash(virtual_key)
                self.ring[hash_key] = node.node_id
            
            self.sorted_keys = sorted(self.ring.keys())
    
    def remove_node(self, node_id: str):
        with self._lock:
            keys_to_remove = [
                k for k, v in self.ring.items()
                if v == node_id
            ]
            for k in keys_to_remove:
                del self.ring[k]
            
            self.sorted_keys = sorted(self.ring.keys())
    
    def get_node(self, key: str) -> Optional[str]:
        with self._lock:
            if not self.ring:
                return None
            
            hash_key = self._hash(key)
            idx = bisect_right(self.sorted_keys, hash_key)
            
            if idx >= len(self.sorted_keys):
                idx = 0
            
            return self.ring[self.sorted_keys[idx]]
    
    def get_nodes(self, key: str, count: int) -> List[str]:
        with self._lock:
            if not self.ring:
                return []
            
            hash_key = self._hash(key)
            idx = bisect_right(self.sorted_keys, hash_key)
            
            nodes = []
            seen = set()
            
            for i in range(len(self.sorted_keys)):
                ring_idx = (idx + i) % len(self.sorted_keys)
                node_id = self.ring[self.sorted_keys[ring_idx]]
                
                if node_id not in seen:
                    nodes.append(node_id)
                    seen.add(node_id)
                
                if len(nodes) >= count:
                    break
            
            return nodes

class ShardManager:
    def __init__(self, replication_factor: int = 3):
        self.replication_factor = replication_factor
        self.hash_ring = ConsistentHash()
        self.nodes: Dict[str, Node] = {}
        self._lock = threading.Lock()
    
    def add_node(self, node: Node):
        with self._lock:
            self.nodes[node.node_id] = node
            self.hash_ring.add_node(node)
    
    def remove_node(self, node_id: str):
        with self._lock:
            if node_id in self.nodes:
                del self.nodes[node_id]
                self.hash_ring.remove_node(node_id)
    
    def get_primary_node(self, key: str) -> Optional[str]:
        return self.hash_ring.get_node(key)
    
    def get_replica_nodes(self, key: str) -> List[str]:
        return self.hash_ring.get_nodes(key, self.replication_factor)

class KVStore:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.data: Dict[str, ReplicaSet] = {}
        self._lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key in self.data:
                return self.data[key].value
            return None
    
    def set(self, key: str, value: Any, version: int = 1) -> bool:
        with self._lock:
            if key in self.data:
                if version <= self.data[key].version:
                    return False
            
            self.data[key] = ReplicaSet(
                key=key,
                value=value,
                version=version
            )
            return True
    
    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self.data:
                del self.data[key]
                return True
            return False
    
    def get_version(self, key: str) -> int:
        with self._lock:
            if key in self.data:
                return self.data[key].version
            return 0

class DistributedKVStore:
    def __init__(self, replication_factor: int = 3):
        self.shard_manager = ShardManager(replication_factor)
        self.stores: Dict[str, KVStore] = {}
        self._lock = threading.Lock()
    
    def add_node(self, node_id: str, host: str = "localhost", port: int = 8000):
        node = Node(node_id=node_id, host=host, port=port)
        self.shard_manager.add_node(node)
        self.stores[node_id] = KVStore(node_id)
    
    def remove_node(self, node_id: str):
        self.shard_manager.remove_node(node_id)
        self.stores.pop(node_id, None)
    
    def get(self, key: str) -> Optional[Any]:
        nodes = self.shard_manager.get_replica_nodes(key)
        
        for node_id in nodes:
            store = self.stores.get(node_id)
            if store:
                value = store.get(key)
                if value is not None:
                    return value
        
        return None
    
    def set(self, key: str, value: Any) -> bool:
        nodes = self.shard_manager.get_replica_nodes(key)
        
        if not nodes:
            return False
        
        version = int(time.time() * 1000)
        success_count = 0
        
        for node_id in nodes:
            store = self.stores.get(node_id)
            if store and store.set(key, value, version):
                success_count += 1
        
        return success_count > 0
    
    def delete(self, key: str) -> bool:
        nodes = self.shard_manager.get_replica_nodes(key)
        success = False
        
        for node_id in nodes:
            store = self.stores.get(node_id)
            if store and store.delete(key):
                success = True
        
        return success
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'total_nodes': len(self.stores),
            'replication_factor': self.shard_manager.replication_factor,
            'node_stats': {
                node_id: len(store.data)
                for node_id, store in self.stores.items()
            }
        }

def main():
    kv_store = DistributedKVStore(replication_factor=3)
    
    kv_store.add_node("node1", port=8001)
    kv_store.add_node("node2", port=8002)
    kv_store.add_node("node3", port=8003)
    kv_store.add_node("node4", port=8004)
    
    print("写入数据...")
    kv_store.set("user:1", {"name": "张三", "age": 25})
    kv_store.set("user:2", {"name": "李四", "age": 30})
    kv_store.set("order:1", {"id": "ORD-001", "amount": 100})
    
    print("\n读取数据:")
    print(f"user:1 = {kv_store.get('user:1')}")
    print(f"user:2 = {kv_store.get('user:2')}")
    print(f"order:1 = {kv_store.get('order:1')}")
    
    print("\n存储统计:")
    stats = kv_store.get_stats()
    print(f"节点数: {stats['total_nodes']}")
    print(f"各节点数据量: {stats['node_stats']}")
    
    print("\n模拟节点故障...")
    kv_store.remove_node("node1")
    
    print(f"user:1 (故障后) = {kv_store.get('user:1')}")

if __name__ == "__main__":
    main()
