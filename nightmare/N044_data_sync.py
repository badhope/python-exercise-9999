# -----------------------------
# 题目：实现分布式数据同步系统。
# 描述：支持数据复制、冲突解决、最终一致性。
# -----------------------------

import time
import threading
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

class SyncStatus(Enum):
    PENDING = "pending"
    SYNCING = "syncing"
    SYNCED = "synced"
    CONFLICT = "conflict"

@dataclass
class VectorClock:
    clocks: Dict[str, int] = field(default_factory=dict)
    
    def increment(self, node_id: str) -> 'VectorClock':
        new_clock = VectorClock(clocks=self.clocks.copy())
        new_clock.clocks[node_id] = new_clock.clocks.get(node_id, 0) + 1
        return new_clock
    
    def merge(self, other: 'VectorClock') -> 'VectorClock':
        merged = VectorClock(clocks=self.clocks.copy())
        for node_id, clock in other.clocks.items():
            merged.clocks[node_id] = max(merged.clocks.get(node_id, 0), clock)
        return merged
    
    def compare(self, other: 'VectorClock') -> int:
        self_greater = False
        other_greater = False
        
        all_nodes = set(self.clocks.keys()) | set(other.clocks.keys())
        
        for node_id in all_nodes:
            self_val = self.clocks.get(node_id, 0)
            other_val = other.clocks.get(node_id, 0)
            
            if self_val > other_val:
                self_greater = True
            elif other_val > self_val:
                other_greater = True
        
        if self_greater and not other_greater:
            return 1
        elif other_greater and not self_greater:
            return -1
        else:
            return 0
    
    def to_dict(self) -> Dict[str, int]:
        return self.clocks.copy()

@dataclass
class DataItem:
    key: str
    value: Any
    version: VectorClock
    timestamp: float
    node_id: str
    tombstone: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'key': self.key,
            'value': self.value,
            'version': self.version.to_dict(),
            'timestamp': self.timestamp,
            'node_id': self.node_id,
            'tombstone': self.tombstone
        }

@dataclass
class SyncLog:
    log_id: str
    operation: str
    key: str
    value: Any
    version: VectorClock
    timestamp: float
    node_id: str

class DataNode:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.data: Dict[str, DataItem] = {}
        self.log: List[SyncLog] = []
        self._lock = threading.Lock()
        self._log_counter = 0
    
    def put(self, key: str, value: Any) -> DataItem:
        with self._lock:
            existing = self.data.get(key)
            
            if existing:
                version = existing.version.increment(self.node_id)
            else:
                version = VectorClock().increment(self.node_id)
            
            item = DataItem(
                key=key,
                value=value,
                version=version,
                timestamp=time.time(),
                node_id=self.node_id
            )
            
            self.data[key] = item
            
            self._log_counter += 1
            self.log.append(SyncLog(
                log_id=f"log-{self._log_counter}",
                operation="put",
                key=key,
                value=value,
                version=version,
                timestamp=item.timestamp,
                node_id=self.node_id
            ))
            
            return item
    
    def get(self, key: str) -> Optional[DataItem]:
        with self._lock:
            return self.data.get(key)
    
    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self.data:
                item = self.data[key]
                item.tombstone = True
                item.version = item.version.increment(self.node_id)
                item.timestamp = time.time()
                return True
            return False
    
    def merge(self, items: List[DataItem]) -> List[str]:
        conflicts = []
        
        with self._lock:
            for item in items:
                existing = self.data.get(item.key)
                
                if existing:
                    cmp = existing.version.compare(item.version)
                    
                    if cmp == 0:
                        conflicts.append(item.key)
                        self._resolve_conflict(existing, item)
                    elif cmp < 0:
                        self.data[item.key] = item
                else:
                    self.data[item.key] = item
        
        return conflicts
    
    def _resolve_conflict(self, local: DataItem, remote: DataItem):
        if local.timestamp > remote.timestamp:
            pass
        else:
            self.data[remote.key] = remote
    
    def get_changes(self, since: float) -> List[DataItem]:
        with self._lock:
            return [
                item for item in self.data.values()
                if item.timestamp > since
            ]

class SyncCoordinator:
    def __init__(self):
        self.nodes: Dict[str, DataNode] = {}
        self._sync_interval = 5.0
        self._running = False
        self._sync_thread: Optional[threading.Thread] = None
    
    def add_node(self, node: DataNode):
        self.nodes[node.node_id] = node
    
    def start_sync(self):
        self._running = True
        self._sync_thread = threading.Thread(target=self._sync_loop)
        self._sync_thread.daemon = True
        self._sync_thread.start()
    
    def stop_sync(self):
        self._running = False
        if self._sync_thread:
            self._sync_thread.join(timeout=5.0)
    
    def _sync_loop(self):
        while self._running:
            self._sync_all_nodes()
            time.sleep(self._sync_interval)
    
    def _sync_all_nodes(self):
        for node_id, node in self.nodes.items():
            changes = node.get_changes(time.time() - self._sync_interval * 2)
            
            if changes:
                for other_id, other_node in self.nodes.items():
                    if other_id != node_id:
                        other_node.merge(changes)
    
    def force_sync(self):
        self._sync_all_nodes()
    
    def get_cluster_state(self) -> Dict[str, Any]:
        return {
            node_id: {
                'data_count': len(node.data),
                'keys': list(node.data.keys())
            }
            for node_id, node in self.nodes.items()
        }

def main():
    coordinator = SyncCoordinator()
    
    node1 = DataNode("node-1")
    node2 = DataNode("node-2")
    node3 = DataNode("node-3")
    
    coordinator.add_node(node1)
    coordinator.add_node(node2)
    coordinator.add_node(node3)
    
    print("写入数据...")
    node1.put("key-1", "value-1")
    node2.put("key-2", "value-2")
    node3.put("key-3", "value-3")
    
    print("\n同步前各节点数据:")
    for node_id, node in coordinator.nodes.items():
        keys = list(node.data.keys())
        print(f"  {node_id}: {keys}")
    
    print("\n执行同步...")
    coordinator.force_sync()
    
    print("\n同步后各节点数据:")
    for node_id, node in coordinator.nodes.items():
        keys = list(node.data.keys())
        print(f"  {node_id}: {keys}")
    
    print("\n模拟冲突:")
    node1.put("conflict-key", "value-from-node1")
    node2.put("conflict-key", "value-from-node2")
    
    coordinator.force_sync()
    
    for node_id, node in coordinator.nodes.items():
        item = node.get("conflict-key")
        if item:
            print(f"  {node_id}: conflict-key = {item.value}")

if __name__ == "__main__":
    main()
