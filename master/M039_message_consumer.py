# -----------------------------
# 题目：实现消息消费者。
# -----------------------------

import threading
import queue
import time
from enum import Enum

class MessageStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Message:
    def __init__(self, topic, body, message_id=None):
        self.topic = topic
        self.body = body
        self.message_id = message_id or str(id(self))
        self.status = MessageStatus.PENDING
        self.retry_count = 0

class MessageConsumer:
    def __init__(self, max_retries=3):
        self.queue = queue.Queue()
        self.max_retries = max_retries
        self.handlers = {}
        self.running = False
        self.thread = None
    
    def subscribe(self, topic, handler):
        self.handlers[topic] = handler
    
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._consume_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
    
    def _consume_loop(self):
        while self.running:
            try:
                message = self.queue.get(timeout=1)
                self._process_message(message)
            except queue.Empty:
                continue
    
    def _process_message(self, message):
        message.status = MessageStatus.PROCESSING
        
        handler = self.handlers.get(message.topic)
        if not handler:
            print(f"No handler for topic: {message.topic}")
            message.status = MessageStatus.FAILED
            return
        
        try:
            handler(message.body)
            message.status = MessageStatus.COMPLETED
        except Exception as e:
            print(f"Error processing message: {e}")
            message.retry_count += 1
            
            if message.retry_count < self.max_retries:
                message.status = MessageStatus.PENDING
                self.queue.put(message)
            else:
                message.status = MessageStatus.FAILED

def handle_user_created(body):
    print(f"Processing user: {body}")

def handle_order_created(body):
    print(f"Processing order: {body}")

if __name__ == "__main__":
    consumer = MessageConsumer(max_retries=3)
    consumer.subscribe("user.created", handle_user_created)
    consumer.subscribe("order.created", handle_order_created)
    
    consumer.start()
    
    consumer.queue.put(Message("user.created", {"username": "john"}))
    consumer.queue.put(Message("order.created", {"order_id": "12345"}))
    
    time.sleep(1)
    consumer.stop()
    print("Consumer stopped")
