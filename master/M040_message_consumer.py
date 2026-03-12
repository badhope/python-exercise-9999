# -----------------------------
# 题目：实现消息队列消费者。
# 描述：支持消息消费、确认机制、重试策略。
# -----------------------------

import time
import threading
import json
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass, field
from enum import Enum
from queue import Queue, Empty
from collections import defaultdict

class MessageStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"

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
    processing_started: Optional[float] = None
    error_message: Optional[str] = None

class DeadLetterQueue:
    def __init__(self):
        self.messages: List[Message] = []
        self._lock = threading.Lock()
    
    def add(self, message: Message):
        with self._lock:
            message.status = MessageStatus.FAILED
            self.messages.append(message)
    
    def get_messages(self) -> List[Message]:
        with self._lock:
            return self.messages.copy()
    
    def size(self) -> int:
        with self._lock:
            return len(self.messages)

class MessageQueue:
    def __init__(self):
        self.queues: Dict[str, Queue] = defaultdict(Queue)
        self._message_counter = 0
        self._lock = threading.Lock()
    
    def publish(self, topic: str, body: Any, headers: Dict = None) -> str:
        with self._lock:
            self._message_counter += 1
            message_id = f"msg-{int(time.time())}-{self._message_counter}"
        
        message = Message(
            message_id=message_id,
            topic=topic,
            body=body,
            headers=headers or {}
        )
        
        self.queues[topic].put(message)
        return message_id
    
    def consume(self, topic: str, timeout: float = 1.0) -> Optional[Message]:
        try:
            message = self.queues[topic].get(timeout=timeout)
            message.status = MessageStatus.PROCESSING
            message.processing_started = time.time()
            return message
        except Empty:
            return None
    
    def ack(self, message: Message):
        message.status = MessageStatus.COMPLETED
    
    def nack(self, message: Message, requeue: bool = True):
        message.retry_count += 1
        
        if message.retry_count >= message.max_retries:
            message.status = MessageStatus.FAILED
        elif requeue:
            message.status = MessageStatus.RETRY
            self.queues[message.topic].put(message)

class Consumer:
    def __init__(
        self,
        queue: MessageQueue,
        topic: str,
        handler: Callable[[Message], bool],
        dlq: DeadLetterQueue = None,
        prefetch: int = 1
    ):
        self.queue = queue
        self.topic = topic
        self.handler = handler
        self.dlq = dlq or DeadLetterQueue()
        self.prefetch = prefetch
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None
        self._processed_count = 0
        self._error_count = 0
    
    def start(self):
        self._running = True
        self._worker_thread = threading.Thread(target=self._consume_loop)
        self._worker_thread.daemon = True
        self._worker_thread.start()
    
    def stop(self):
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=5.0)
    
    def _consume_loop(self):
        while self._running:
            message = self.queue.consume(self.topic, timeout=1.0)
            if message:
                self._process_message(message)
    
    def _process_message(self, message: Message):
        try:
            success = self.handler(message)
            
            if success:
                self.queue.ack(message)
                self._processed_count += 1
            else:
                self._handle_failure(message)
        
        except Exception as e:
            message.error_message = str(e)
            self._handle_failure(message)
    
    def _handle_failure(self, message: Message):
        self._error_count += 1
        
        if message.retry_count >= message.max_retries:
            self.dlq.add(message)
        else:
            self.queue.nack(message, requeue=True)
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'topic': self.topic,
            'processed': self._processed_count,
            'errors': self._error_count,
            'dlq_size': self.dlq.size()
        }

class ConsumerGroup:
    def __init__(self, queue: MessageQueue, dlq: DeadLetterQueue = None):
        self.queue = queue
        self.dlq = dlq or DeadLetterQueue()
        self.consumers: Dict[str, Consumer] = {}
        self._lock = threading.Lock()
    
    def subscribe(
        self,
        topic: str,
        handler: Callable[[Message], bool],
        num_consumers: int = 1
    ):
        with self._lock:
            for i in range(num_consumers):
                consumer_id = f"{topic}-consumer-{i}"
                consumer = Consumer(
                    self.queue,
                    topic,
                    handler,
                    self.dlq
                )
                self.consumers[consumer_id] = consumer
    
    def start_all(self):
        for consumer in self.consumers.values():
            consumer.start()
    
    def stop_all(self):
        for consumer in self.consumers.values():
            consumer.stop()
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'consumers': len(self.consumers),
            'dlq_size': self.dlq.size(),
            'consumer_stats': {
                cid: c.get_stats() for cid, c in self.consumers.items()
            }
        }

def main():
    mq = MessageQueue()
    dlq = DeadLetterQueue()
    
    processed_messages = []
    
    def order_handler(message: Message) -> bool:
        data = message.body
        print(f"处理订单: {data}")
        
        if data.get('should_fail') and message.retry_count < 2:
            print(f"  模拟失败 (重试 {message.retry_count})")
            return False
        
        processed_messages.append(data)
        return True
    
    def notification_handler(message: Message) -> bool:
        print(f"发送通知: {message.body}")
        return True
    
    group = ConsumerGroup(mq, dlq)
    group.subscribe('orders', order_handler, num_consumers=2)
    group.subscribe('notifications', notification_handler)
    
    group.start_all()
    
    mq.publish('orders', {'order_id': 'ORD-001', 'amount': 100})
    mq.publish('orders', {'order_id': 'ORD-002', 'should_fail': True})
    mq.publish('orders', {'order_id': 'ORD-003', 'amount': 200})
    mq.publish('notifications', {'type': 'email', 'to': 'user@example.com'})
    
    time.sleep(2)
    
    group.stop_all()
    
    print(f"\n消费者统计: {group.get_stats()}")
    print(f"死信队列: {[m.body for m in dlq.get_messages()]}")

if __name__ == "__main__":
    main()
