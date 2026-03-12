# -----------------------------
# 题目：实现分布式消息队列。
# 描述：支持消息分区、消费者组、消息持久化。
# -----------------------------

import time
import threading
import hashlib
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from queue import Queue
from collections import defaultdict

class MessageStatus(Enum):
    PENDING = "pending"
    DELIVERED = "delivered"
    ACKNOWLEDGED = "acknowledged"
    FAILED = "failed"

@dataclass
class Message:
    message_id: str
    topic: str
    partition: int
    key: Optional[str]
    value: Any
    headers: Dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    status: MessageStatus = MessageStatus.PENDING
    offset: int = 0

@dataclass
class Partition:
    partition_id: int
    topic: str
    messages: List[Message] = field(default_factory=list)
    commit_offset: int = 0
    _lock: threading.Lock = field(default_factory=threading.Lock)
    
    def append(self, message: Message) -> int:
        with self._lock:
            message.offset = len(self.messages)
            self.messages.append(message)
            return message.offset
    
    def fetch(self, offset: int, max_messages: int = 10) -> List[Message]:
        with self._lock:
            return self.messages[offset:offset + max_messages]
    
    def commit(self, offset: int):
        with self._lock:
            self.commit_offset = max(self.commit_offset, offset)

@dataclass
class ConsumerGroup:
    group_id: str
    topic: str
    consumers: Dict[str, int] = field(default_factory=dict)
    partition_assignments: Dict[int, str] = field(default_factory=dict)
    offsets: Dict[int, int] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock)
    
    def join(self, consumer_id: str):
        with self._lock:
            self.consumers[consumer_id] = int(time.time())
            self._rebalance()
    
    def leave(self, consumer_id: str):
        with self._lock:
            self.consumers.pop(consumer_id, None)
            self._rebalance()
    
    def _rebalance(self):
        partitions = list(self.partition_assignments.keys())
        consumers = list(self.consumers.keys())
        
        self.partition_assignments.clear()
        
        for i, partition in enumerate(partitions):
            consumer = consumers[i % len(consumers)] if consumers else None
            if consumer:
                self.partition_assignments[partition] = consumer
    
    def get_assigned_partitions(self, consumer_id: str) -> List[int]:
        with self._lock:
            return [
                p for p, c in self.partition_assignments.items()
                if c == consumer_id
            ]
    
    def update_offset(self, partition: int, offset: int):
        with self._lock:
            self.offsets[partition] = offset
    
    def get_offset(self, partition: int) -> int:
        with self._lock:
            return self.offsets.get(partition, 0)

class Topic:
    def __init__(self, name: str, num_partitions: int = 3):
        self.name = name
        self.num_partitions = num_partitions
        self.partitions: Dict[int, Partition] = {
            i: Partition(partition_id=i, topic=name)
            for i in range(num_partitions)
        }
    
    def get_partition(self, key: str = None) -> int:
        if key is None:
            import random
            return random.randint(0, self.num_partitions - 1)
        
        hash_val = int(hashlib.md5(key.encode()).hexdigest(), 16)
        return hash_val % self.num_partitions

class DistributedMessageQueue:
    def __init__(self):
        self.topics: Dict[str, Topic] = {}
        self.consumer_groups: Dict[str, ConsumerGroup] = {}
        self._message_counter = 0
        self._lock = threading.Lock()
    
    def create_topic(self, name: str, num_partitions: int = 3):
        with self._lock:
            self.topics[name] = Topic(name, num_partitions)
    
    def produce(
        self,
        topic_name: str,
        value: Any,
        key: str = None,
        headers: Dict = None
    ) -> Message:
        topic = self.topics.get(topic_name)
        if not topic:
            raise ValueError(f"Topic {topic_name} not found")
        
        with self._lock:
            self._message_counter += 1
            message_id = f"msg-{int(time.time())}-{self._message_counter}"
        
        partition_idx = topic.get_partition(key)
        partition = topic.partitions[partition_idx]
        
        message = Message(
            message_id=message_id,
            topic=topic_name,
            partition=partition_idx,
            key=key,
            value=value,
            headers=headers or {}
        )
        
        partition.append(message)
        return message
    
    def create_consumer_group(self, group_id: str, topic_name: str):
        topic = self.topics.get(topic_name)
        if not topic:
            raise ValueError(f"Topic {topic_name} not found")
        
        with self._lock:
            group = ConsumerGroup(group_id=group_id, topic=topic_name)
            for partition_id in topic.partitions:
                group.partition_assignments[partition_id] = None
            self.consumer_groups[group_id] = group
    
    def join_group(self, group_id: str, consumer_id: str):
        group = self.consumer_groups.get(group_id)
        if group:
            group.join(consumer_id)
    
    def leave_group(self, group_id: str, consumer_id: str):
        group = self.consumer_groups.get(group_id)
        if group:
            group.leave(consumer_id)
    
    def consume(
        self,
        group_id: str,
        consumer_id: str,
        max_messages: int = 10
    ) -> List[Message]:
        group = self.consumer_groups.get(group_id)
        if not group:
            return []
        
        topic = self.topics.get(group.topic)
        if not topic:
            return []
        
        assigned_partitions = group.get_assigned_partitions(consumer_id)
        messages = []
        
        for partition_id in assigned_partitions:
            partition = topic.partitions[partition_id]
            offset = group.get_offset(partition_id)
            
            partition_messages = partition.fetch(offset, max_messages)
            messages.extend(partition_messages)
        
        return messages[:max_messages]
    
    def commit(self, group_id: str, partition: int, offset: int):
        group = self.consumer_groups.get(group_id)
        if group:
            group.update_offset(partition, offset)
            
            topic = self.topics.get(group.topic)
            if topic:
                topic.partitions[partition].commit(offset)
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'topics': {
                name: {
                    'partitions': len(topic.partitions),
                    'total_messages': sum(
                        len(p.messages) for p in topic.partitions.values()
                    )
                }
                for name, topic in self.topics.items()
            },
            'consumer_groups': len(self.consumer_groups)
        }

def main():
    queue = DistributedMessageQueue()
    
    queue.create_topic("orders", num_partitions=3)
    queue.create_topic("notifications", num_partitions=2)
    
    print("生产消息...")
    for i in range(10):
        msg = queue.produce("orders", {"order_id": f"ORD-{i}", "amount": i * 100}, key=f"user-{i % 3}")
        print(f"  发送到分区 {msg.partition}: {msg.value}")
    
    queue.create_consumer_group("order-processors", "orders")
    queue.join_group("order-processors", "consumer-1")
    queue.join_group("order-processors", "consumer-2")
    
    print("\n消费者1消费:")
    messages = queue.consume("order-processors", "consumer-1")
    for msg in messages:
        print(f"  分区{msg.partition} offset={msg.offset}: {msg.value}")
    
    print("\n队列统计:")
    stats = queue.get_stats()
    print(f"  Topics: {stats['topics']}")
    print(f"  消费者组: {stats['consumer_groups']}")

if __name__ == "__main__":
    main()
