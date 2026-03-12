# -----------------------------
# 题目：实现简单的消息队列。
# 描述：支持发布订阅、消息持久化。
# -----------------------------

import queue
import threading
import json
import os

class Message:
    def __init__(self, topic, payload, message_id=None):
        self.topic = topic
        self.payload = payload
        self.message_id = message_id or id(self)
        self.timestamp = time.time()

class MessageQueue:
    def __init__(self, storage_dir=None):
        self.queues = {}
        self.subscribers = {}
        self.storage_dir = storage_dir
        self._lock = threading.Lock()
        
        if storage_dir:
            os.makedirs(storage_dir, exist_ok=True)
    
    def publish(self, topic, payload):
        message = Message(topic, payload)
        
        with self._lock:
            if topic not in self.queues:
                self.queues[topic] = queue.Queue()
            
            self.queues[topic].put(message)
            
            if topic in self.subscribers:
                for subscriber in self.subscribers[topic]:
                    subscriber(message)
            
            if self.storage_dir:
                self._persist(message)
        
        return message.message_id
    
    def subscribe(self, topic, callback):
        with self._lock:
            if topic not in self.subscribers:
                self.subscribers[topic] = []
            self.subscribers[topic].append(callback)
    
    def consume(self, topic, timeout=None):
        with self._lock:
            if topic not in self.queues:
                self.queues[topic] = queue.Queue()
        
        try:
            return self.queues[topic].get(timeout=timeout)
        except queue.Empty:
            return None
    
    def _persist(self, message):
        filepath = os.path.join(self.storage_dir, f"{message.topic}.log")
        with open(filepath, 'a') as f:
            f.write(json.dumps({
                'id': message.message_id,
                'topic': message.topic,
                'payload': message.payload,
                'timestamp': message.timestamp
            }) + '\n')

class Consumer(threading.Thread):
    def __init__(self, mq, topic, name):
        super().__init__()
        self.mq = mq
        self.topic = topic
        self.name = name
        self.daemon = True
    
    def run(self):
        while True:
            message = self.mq.consume(self.topic, timeout=1)
            if message:
                print(f"[{self.name}] 收到消息: {message.payload}")

def main():
    mq = MessageQueue()
    
    def log_message(message):
        print(f"[日志] {message.topic}: {message.payload}")
    
    mq.subscribe('orders', log_message)
    
    mq.publish('orders', {'order_id': 1, 'item': '笔记本'})
    mq.publish('orders', {'order_id': 2, 'item': '手机'})


if __name__ == "__main__":
    import time
    main()
