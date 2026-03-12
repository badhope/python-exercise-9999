# -----------------------------
# 题目：实现简单的消息队列。
# -----------------------------

import queue
import threading
import time
from dataclasses import dataclass
from typing import Callable, Dict, List
from enum import Enum

class MessageStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Message:
    id: int
    topic: str
    payload: dict
    status: MessageStatus = MessageStatus.PENDING
    retry_count: int = 0
    max_retries: int = 3
    created_at: float = None
    processed_at: float = None

class MessageQueue:
    def __init__(self):
        self.queues: Dict[str, queue.Queue] = {}
        self.handlers: Dict[str, Callable] = {}
        self.messages: Dict[int, Message] = {}
        self.next_id = 1
        self.lock = threading.Lock()
        self.workers: List[threading.Thread] = []
        self.running = False
    
    def create_topic(self, topic: str):
        if topic not in self.queues:
            self.queues[topic] = queue.Queue()
    
    def subscribe(self, topic: str, handler: Callable):
        self.handlers[topic] = handler
        self.create_topic(topic)
    
    def publish(self, topic: str, payload: dict) -> int:
        with self.lock:
            message_id = self.next_id
            self.next_id += 1
        
        message = Message(
            id=message_id,
            topic=topic,
            payload=payload,
            created_at=time.time()
        )
        
        self.messages[message_id] = message
        self.create_topic(topic)
        self.queues[topic].put(message)
        
        return message_id
    
    def start(self, num_workers: int = 2):
        self.running = True
        for _ in range(num_workers):
            worker = threading.Thread(target=self._worker, daemon=True)
            worker.start()
            self.workers.append(worker)
    
    def stop(self):
        self.running = False
        for topic_queue in self.queues.values():
            topic_queue.put(None)
        for worker in self.workers:
            worker.join(timeout=1)
    
    def get_message_status(self, message_id: int) -> MessageStatus:
        message = self.messages.get(message_id)
        return message.status if message else None
    
    def get_pending_count(self, topic: str) -> int:
        if topic in self.queues:
            return self.queues[topic].qsize()
        return 0
    
    def _worker(self):
        while self.running:
            for topic, topic_queue in self.queues.items():
                try:
                    message = topic_queue.get(timeout=0.1)
                    if message is None:
                        continue
                    
                    self._process_message(message, topic)
                except queue.Empty:
                    continue
    
    def _process_message(self, message: Message, topic: str):
        message.status = MessageStatus.PROCESSING
        
        try:
            handler = self.handlers.get(topic)
            if handler:
                handler(message.payload)
            message.status = MessageStatus.COMPLETED
            message.processed_at = time.time()
        except Exception as e:
            message.retry_count += 1
            if message.retry_count < message.max_retries:
                message.status = MessageStatus.PENDING
                self.queues[topic].put(message)
            else:
                message.status = MessageStatus.FAILED

class TopicManager:
    def __init__(self, mq: MessageQueue):
        self.mq = mq
        self.subscriptions: Dict[str, List[Callable]] = {}
    
    def subscribe(self, topic: str, handler: Callable):
        if topic not in self.subscriptions:
            self.subscriptions[topic] = []
        self.subscriptions[topic].append(handler)
        
        def wrapper(payload):
            for h in self.subscriptions[topic]:
                h(payload)
        
        self.mq.subscribe(topic, wrapper)
    
    def publish(self, topic: str, payload: dict):
        return self.mq.publish(topic, payload)

def main():
    mq = MessageQueue()
    
    def order_handler(payload):
        print(f"处理订单: {payload}")
    
    def notification_handler(payload):
        print(f"发送通知: {payload}")
    
    mq.subscribe('orders', order_handler)
    mq.subscribe('notifications', notification_handler)
    
    mq.start(num_workers=2)
    
    print("=== 发布消息 ===")
    order_id = mq.publish('orders', {'order_id': 1001, 'user': '张三', 'total': 299.99})
    print(f"订单消息ID: {order_id}")
    
    notif_id = mq.publish('notifications', {'type': 'email', 'to': 'user@example.com'})
    print(f"通知消息ID: {notif_id}")
    
    time.sleep(1)
    
    print(f"\n订单状态: {mq.get_message_status(order_id).value}")
    print(f"通知状态: {mq.get_message_status(notif_id).value}")
    
    mq.stop()


if __name__ == "__main__":
    main()
