# -----------------------------
# 题目：实现简单的分布式消息系统。
# 描述：支持消息分区、消费组、偏移量管理。
# -----------------------------

import threading
import time
from collections import defaultdict
from enum import Enum

class MessageStatus(Enum):
    PENDING = "pending"
    CONSUMED = "consumed"
    FAILED = "failed"

class Message:
    def __init__(self, topic, partition, offset, key, value):
        self.topic = topic
        self.partition = partition
        self.offset = offset
        self.key = key
        self.value = value
        self.timestamp = time.time()
        self.status = MessageStatus.PENDING

class Partition:
    def __init__(self, partition_id):
        self.partition_id = partition_id
        self.messages = []
        self._lock = threading.Lock()
        self._offset = 0
    
    def append(self, key, value):
        with self._lock:
            message = Message(None, self.partition_id, self._offset, key, value)
            self.messages.append(message)
            self._offset += 1
            return message
    
    def get_messages(self, offset, limit=100):
        with self._lock:
            return self.messages[offset:offset + limit]

class Topic:
    def __init__(self, name, num_partitions=3):
        self.name = name
        self.partitions = [Partition(i) for i in range(num_partitions)]
    
    def get_partition(self, key):
        if key is None:
            import random
            return random.choice(self.partitions)
        return self.partitions[hash(key) % len(self.partitions)]
    
    def produce(self, key, value):
        partition = self.get_partition(key)
        return partition.append(key, value)

class ConsumerGroup:
    def __init__(self, group_id, topic):
        self.group_id = group_id
        self.topic = topic
        self.offsets = defaultdict(int)
        self.assignments = {}
        self._lock = threading.Lock()
    
    def assign_partition(self, consumer_id, partition_id):
        with self._lock:
            self.assignments[consumer_id] = partition_id
    
    def consume(self, consumer_id, limit=10):
        with self._lock:
            partition_id = self.assignments.get(consumer_id)
            if partition_id is None:
                return []
            
            partition = self.topic.partitions[partition_id]
            offset = self.offsets[partition_id]
            
            messages = partition.get_messages(offset, limit)
            if messages:
                self.offsets[partition_id] = messages[-1].offset + 1
            
            return messages
    
    def commit(self, partition_id, offset):
        with self._lock:
            self.offsets[partition_id] = offset

class MessageBroker:
    def __init__(self):
        self.topics = {}
        self.consumer_groups = {}
        self._lock = threading.Lock()
    
    def create_topic(self, name, num_partitions=3):
        with self._lock:
            if name not in self.topics:
                self.topics[name] = Topic(name, num_partitions)
        return self.topics[name]
    
    def produce(self, topic_name, key, value):
        topic = self.topics.get(topic_name)
        if topic:
            return topic.produce(key, value)
        return None
    
    def create_consumer_group(self, group_id, topic_name):
        with self._lock:
            key = f"{group_id}:{topic_name}"
            if key not in self.consumer_groups:
                topic = self.topics.get(topic_name)
                if topic:
                    self.consumer_groups[key] = ConsumerGroup(group_id, topic)
        return self.consumer_groups.get(key)
    
    def subscribe(self, group_id, topic_name, consumer_id):
        key = f"{group_id}:{topic_name}"
        group = self.consumer_groups.get(key)
        if group:
            topic = self.topics.get(topic_name)
            if topic:
                partition_id = hash(consumer_id) % len(topic.partitions)
                group.assign_partition(consumer_id, partition_id)

def main():
    broker = MessageBroker()
    broker.create_topic("orders", 3)
    
    for i in range(5):
        broker.produce("orders", f"order_{i}", {"order_id": i, "item": f"商品{i}"})
    
    group = broker.create_consumer_group("order-processors", "orders")
    group.subscribe("order-processors", "orders", "consumer-1")
    
    messages = group.consume("consumer-1")
    print("消费消息:")
    for msg in messages:
        print(f"  分区{msg.partition}, 偏移{msg.offset}: {msg.value}")


if __name__ == "__main__":
    main()
