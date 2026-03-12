# -----------------------------
# 题目：实现分布式文件系统。
# 描述：支持文件分块、副本复制、负载均衡。
# -----------------------------

import time
import threading
import hashlib
import random
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from bisect import bisect_right

@dataclass
class FileBlock:
    block_id: str
    file_id: str
    index: int
    size: int
    checksum: str
    locations: List[str] = field(default_factory=list)

@dataclass
class FileMetadata:
    file_id: str
    name: str
    size: int
    block_size: int
    blocks: List[FileBlock] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    modified_at: float = field(default_factory=time.time)
    replication: int = 3

@dataclass
class DataNode:
    node_id: str
    host: str
    port: int
    capacity: int
    used: int = 0
    blocks: List[str] = field(default_factory=list)
    last_heartbeat: float = field(default_factory=time.time)
    status: str = "alive"

class ConsistentHash:
    def __init__(self, virtual_nodes: int = 100):
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
        keys_to_remove = [k for k, v in self.ring.items() if v == node_id]
        for k in keys_to_remove:
            del self.ring[k]
        self.sorted_keys = sorted(self.ring.keys())
    
    def get_nodes(self, key: str, count: int) -> List[str]:
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

class NameNode:
    def __init__(self, block_size: int = 64 * 1024 * 1024, replication: int = 3):
        self.block_size = block_size
        self.replication = replication
        self.files: Dict[str, FileMetadata] = {}
        self.data_nodes: Dict[str, DataNode] = {}
        self.hash_ring = ConsistentHash()
        self._lock = threading.RLock()
    
    def register_data_node(self, node: DataNode):
        with self._lock:
            self.data_nodes[node.node_id] = node
            self.hash_ring.add_node(node.node_id)
    
    def unregister_data_node(self, node_id: str):
        with self._lock:
            self.data_nodes.pop(node_id, None)
            self.hash_ring.remove_node(node_id)
    
    def create_file(self, name: str, size: int) -> FileMetadata:
        file_id = f"file-{hashlib.md5(name.encode()).hexdigest()[:12]}"
        
        num_blocks = (size + self.block_size - 1) // self.block_size
        
        metadata = FileMetadata(
            file_id=file_id,
            name=name,
            size=size,
            block_size=self.block_size,
            replication=self.replication
        )
        
        for i in range(num_blocks):
            block_id = f"{file_id}-block-{i}"
            block_size = min(self.block_size, size - i * self.block_size)
            
            locations = self.hash_ring.get_nodes(block_id, self.replication)
            
            block = FileBlock(
                block_id=block_id,
                file_id=file_id,
                index=i,
                size=block_size,
                checksum="",
                locations=locations
            )
            
            metadata.blocks.append(block)
        
        with self._lock:
            self.files[file_id] = metadata
        
        return metadata
    
    def get_file(self, file_id: str) -> Optional[FileMetadata]:
        return self.files.get(file_id)
    
    def get_file_by_name(self, name: str) -> Optional[FileMetadata]:
        for f in self.files.values():
            if f.name == name:
                return f
        return None
    
    def delete_file(self, file_id: str) -> bool:
        with self._lock:
            if file_id in self.files:
                del self.files[file_id]
                return True
            return False
    
    def get_block_locations(self, block_id: str) -> List[str]:
        return self.hash_ring.get_nodes(block_id, self.replication)
    
    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            total_capacity = sum(n.capacity for n in self.data_nodes.values())
            total_used = sum(n.used for n in self.data_nodes.values())
            
            return {
                'total_files': len(self.files),
                'total_blocks': sum(len(f.blocks) for f in self.files.values()),
                'data_nodes': len(self.data_nodes),
                'total_capacity': total_capacity,
                'total_used': total_used,
                'usage_percent': f"{total_used / total_capacity * 100:.1f}%" if total_capacity else "0%"
            }

class DataNodeClient:
    def __init__(self, node: DataNode):
        self.node = node
        self._storage: Dict[str, bytes] = {}
        self._lock = threading.Lock()
    
    def write_block(self, block_id: str, data: bytes) -> bool:
        with self._lock:
            self._storage[block_id] = data
            self.node.used += len(data)
            self.node.blocks.append(block_id)
            return True
    
    def read_block(self, block_id: str) -> Optional[bytes]:
        with self._lock:
            return self._storage.get(block_id)
    
    def delete_block(self, block_id: str) -> bool:
        with self._lock:
            if block_id in self._storage:
                size = len(self._storage[block_id])
                del self._storage[block_id]
                self.node.used -= size
                self.node.blocks.remove(block_id)
                return True
            return False

class DistributedFileSystem:
    def __init__(self):
        self.name_node = NameNode()
        self.data_node_clients: Dict[str, DataNodeClient] = {}
    
    def add_data_node(self, node_id: str, host: str, port: int, capacity: int):
        node = DataNode(node_id=node_id, host=host, port=port, capacity=capacity)
        self.name_node.register_data_node(node)
        self.data_node_clients[node_id] = DataNodeClient(node)
    
    def create_file(self, name: str, data: bytes) -> FileMetadata:
        metadata = self.name_node.create_file(name, len(data))
        
        for block in metadata.blocks:
            start = block.index * metadata.block_size
            end = min(start + metadata.block_size, len(data))
            block_data = data[start:end]
            
            block.checksum = hashlib.md5(block_data).hexdigest()
            
            for location in block.locations:
                client = self.data_node_clients.get(location)
                if client:
                    client.write_block(block.block_id, block_data)
        
        return metadata
    
    def read_file(self, name: str) -> Optional[bytes]:
        metadata = self.name_node.get_file_by_name(name)
        if not metadata:
            return None
        
        data = b''
        
        for block in metadata.blocks:
            block_data = None
            
            for location in block.locations:
                client = self.data_node_clients.get(location)
                if client:
                    block_data = client.read_block(block.block_id)
                    if block_data:
                        break
            
            if block_data:
                data += block_data
            else:
                return None
        
        return data
    
    def delete_file(self, name: str) -> bool:
        metadata = self.name_node.get_file_by_name(name)
        if not metadata:
            return False
        
        for block in metadata.blocks:
            for location in block.locations:
                client = self.data_node_clients.get(location)
                if client:
                    client.delete_block(block.block_id)
        
        return self.name_node.delete_file(metadata.file_id)
    
    def get_stats(self) -> Dict[str, Any]:
        return self.name_node.get_stats()

def main():
    dfs = DistributedFileSystem()
    
    dfs.add_data_node("dn1", "192.168.1.10", 9001, 1024 * 1024 * 1024)
    dfs.add_data_node("dn2", "192.168.1.11", 9001, 1024 * 1024 * 1024)
    dfs.add_data_node("dn3", "192.168.1.12", 9001, 1024 * 1024 * 1024)
    
    print("创建文件...")
    content = b"Hello, Distributed File System!" * 1000
    metadata = dfs.create_file("test.txt", content)
    print(f"  文件ID: {metadata.file_id}")
    print(f"  文件大小: {metadata.size} bytes")
    print(f"  分块数: {len(metadata.blocks)}")
    
    print("\n读取文件...")
    data = dfs.read_file("test.txt")
    if data:
        print(f"  读取成功: {len(data)} bytes")
        print(f"  内容预览: {data[:50]}...")
    
    print("\n存储统计:")
    stats = dfs.get_stats()
    print(f"  文件数: {stats['total_files']}")
    print(f"  分块数: {stats['total_blocks']}")
    print(f"  数据节点: {stats['data_nodes']}")
    print(f"  使用率: {stats['usage_percent']}")

if __name__ == "__main__":
    main()
