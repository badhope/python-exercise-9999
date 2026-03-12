# -----------------------------
# 题目：实现消息队列。
# 描述：支持发布订阅、消息确认、死信队列。
# -----------------------------

import time
import json
import threading
from typing import Dict, List, Callable, Optional, Any
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
    body: Any
    headers: Dict[str, str] = field(default_factory=dict)
    status: MessageStatus = MessageStatus.PENDING
    retry_count: int = 0
    max_retries: int = 3
    created_at: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict:
        return {
            'message_id': self.message_id,
            'topic': self.topic,
            'body': self.body,
            'headers': self.headers,
            'status': self.status.value,
            'retry_count': self.retry_count
        }

class DeadLetterQueue:
    def __init__(self):
        self.messages: List[Message] = []
        self._lock = threading.Lock()
    
    def add(self, message: Message):
        with self._lock:
            message.status = MessageStatus.FAILED
            self.messages.append(message)
    
    def get_messages(self) -> List[Message]:
        return self.messages.copy()
    
    def reprocess(self, message_id: str) -> Optional[Message]:
        with self._lock:
            for i, msg in enumerate(self.messages):
                if msg.message_id == message_id:
                    return self.messages.pop(i)
        return None

class Topic:
    def __init__(self, name: str):
        self.name = name
        self.queue: Queue = Queue()
        self.subscribers: List[Callable] = []
        self._lock = threading.Lock()
    
    def publish(self, message: Message):
        self.queue.put(message)
    
    def subscribe(self, callback: Callable):
        with self._lock:
            self.subscribers.append(callback)
    
    def get_message(self, timeout: float = 1.0) -> Optional[Message]:
        try:
            return self.queue.get(timeout=timeout)
        except:
            return None
    
    def ack(self, message: Message):
        message.status = MessageStatus.ACKNOWLEDGED
    
    def nack(self, message: Message):
        message.status = MessageStatus.PENDING
        message.retry_count += 1

class MessageQueue:
    def __init__(self):
        self.topics: Dict[str, Topic] = {}
        self.dlq = DeadLetterQueue()
        self.message_counter = 0
        self._lock = threading.Lock()
        self._running = False
        self._workers: List[threading.Thread] = []
    
    def create_topic(self, name: str) -> Topic:
        if name not in self.topics:
            self.topics[name] = Topic(name)
        return self.topics[name]
    
    def _generate_message_id(self) -> str:
        with self._lock:
            self.message_counter += 1
            return f"msg-{int(time.time())}-{self.message_counter}"
    
    def publish(self, topic_name: str, body: Any, headers: Dict = None) -> str:
        topic = self.topics.get(topic_name)
        if not topic:
            topic = self.create_topic(topic_name)
        
        message = Message(
            message_id=self._generate_message_id(),
            topic=topic_name,
            body=body,
            headers=headers or {}
        )
        
        topic.publish(message)
        return message.message_id
    
    def subscribe(self, topic_name: str, callback: Callable):
        topic = self.topics.get(topic_name)
        if not topic:
            topic = self.create_topic(topic_name)
        topic.subscribe(callback)
    
    def start_workers(self, num_workers: int = 2):
        self._running = True
        
        for i in range(num_workers):
            worker = threading.Thread(target=self._worker, args=(i,))
            worker.daemon = True
            worker.start()
            self._workers.append(worker)
    
    def stop_workers(self):
        self._running = False
        for worker in self._workers:
            worker.join(timeout=2.0)
        self._workers.clear()
    
    def _worker(self, worker_id: int):
        while self._running:
            for topic_name, topic in self.topics.items():
                message = topic.get_message(timeout=0.1)
                if message:
                    self._process_message(topic, message)
    
    def _process_message(self, topic: Topic, message: Message):
        try:
            for callback in topic.subscribers:
                callback(message.body, message.headers)
            topic.ack(message)
        except Exception as e:
            message.retry_count += 1
            if message.retry_count >= message.max_retries:
                self.dlq.add(message)
            else:
                topic.nack(message)
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'topics': list(self.topics.keys()),
            'dlq_size': len(self.dlq.messages),
            'total_messages': self.message_counter
        }

def main():
    mq = MessageQueue()
    
    received_messages = []
    
    def message_handler(body, headers):
        print(f"收到消息: {body}")
        received_messages.append(body)
    
    mq.subscribe('orders', message_handler)
    mq.subscribe('notifications', message_handler)
    
    msg_id1 = mq.publish('orders', {'order_id': 'ORD-001', 'amount': 100.0})
    msg_id2 = mq.publish('orders', {'order_id': 'ORD-002', 'amount': 200.0})
    msg_id3 = mq.publish('notifications', {'type': 'email', 'to': 'user@example.com'})
    
    print(f"发布消息: {msg_id1}, {msg_id2}, {msg_id3}")
    
    mq.start_workers(num_workers=2)
    time.sleep(1)
    mq.stop_workers()
    
    print(f"\n统计: {mq.get_stats()}")

if __name__ == "__main__":
    main()
