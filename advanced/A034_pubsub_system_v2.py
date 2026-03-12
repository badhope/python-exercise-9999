# -----------------------------
# 题目：实现简单的发布订阅系统。
# -----------------------------

from typing import Callable, Dict, List, Any, Set
from dataclasses import dataclass
from threading import Lock
import time

@dataclass
class Message:
    topic: str
    payload: Any
    timestamp: float
    publisher: str = None

class Subscriber:
    def __init__(self, name: str, handler: Callable[[Message], None]):
        self.name = name
        self.handler = handler
        self.subscriptions: Set[str] = set()
    
    def receive(self, message: Message):
        self.handler(message)

class Publisher:
    def __init__(self, name: str):
        self.name = name
        self.published_count = 0
    
    def publish(self, broker: 'MessageBroker', topic: str, payload: Any) -> int:
        message = Message(
            topic=topic,
            payload=payload,
            timestamp=time.time(),
            publisher=self.name
        )
        self.published_count += 1
        return broker.publish(topic, message)

class MessageBroker:
    def __init__(self):
        self.subscribers: Dict[str, List[Subscriber]] = {}
        self.lock = Lock()
        self.message_count = 0
    
    def subscribe(self, topic: str, subscriber: Subscriber):
        with self.lock:
            if topic not in self.subscribers:
                self.subscribers[topic] = []
            
            if subscriber not in self.subscribers[topic]:
                self.subscribers[topic].append(subscriber)
                subscriber.subscriptions.add(topic)
    
    def unsubscribe(self, topic: str, subscriber: Subscriber):
        with self.lock:
            if topic in self.subscribers and subscriber in self.subscribers[topic]:
                self.subscribers[topic].remove(subscriber)
                subscriber.subscriptions.discard(topic)
    
    def publish(self, topic: str, message: Message) -> int:
        with self.lock:
            subscribers = self.subscribers.get(topic, []).copy()
        
        self.message_count += 1
        
        for subscriber in subscribers:
            try:
                subscriber.receive(message)
            except Exception as e:
                print(f"订阅者 {subscriber.name} 处理消息失败: {e}")
        
        return len(subscribers)
    
    def get_subscribers(self, topic: str) -> List[str]:
        with self.lock:
            return [s.name for s in self.subscribers.get(topic, [])]
    
    def get_topics(self) -> List[str]:
        with self.lock:
            return list(self.subscribers.keys())

class Topic:
    def __init__(self, name: str, broker: MessageBroker):
        self.name = name
        self.broker = broker
    
    def subscribe(self, subscriber: Subscriber):
        self.broker.subscribe(self.name, subscriber)
    
    def unsubscribe(self, subscriber: Subscriber):
        self.broker.unsubscribe(self.name, subscriber)
    
    def publish(self, payload: Any, publisher_name: str = None) -> int:
        message = Message(
            topic=self.name,
            payload=payload,
            timestamp=time.time(),
            publisher=publisher_name
        )
        return self.broker.publish(self.name, message)

class PubSubClient:
    def __init__(self, name: str, broker: MessageBroker):
        self.name = name
        self.broker = broker
        self.subscriber = Subscriber(name, self._handle_message)
        self.messages: List[Message] = []
    
    def _handle_message(self, message: Message):
        self.messages.append(message)
    
    def subscribe(self, topic: str):
        self.broker.subscribe(topic, self.subscriber)
    
    def unsubscribe(self, topic: str):
        self.broker.unsubscribe(topic, self.subscriber)
    
    def publish(self, topic: str, payload: Any):
        message = Message(
            topic=topic,
            payload=payload,
            timestamp=time.time(),
            publisher=self.name
        )
        return self.broker.publish(topic, message)
    
    def get_messages(self) -> List[Message]:
        return self.messages.copy()
    
    def clear_messages(self):
        self.messages.clear()

def main():
    broker = MessageBroker()
    
    def log_handler(message: Message):
        print(f"[日志] {message.topic}: {message.payload}")
    
    def alert_handler(message: Message):
        print(f"[警报] {message.topic}: {message.payload}")
    
    subscriber1 = Subscriber("日志订阅者", log_handler)
    subscriber2 = Subscriber("警报订阅者", alert_handler)
    
    broker.subscribe("system.events", subscriber1)
    broker.subscribe("system.errors", subscriber1)
    broker.subscribe("system.errors", subscriber2)
    
    publisher = Publisher("系统发布者")
    
    print("=== 发布系统事件 ===")
    publisher.publish(broker, "system.events", {"type": "startup", "message": "系统启动"})
    
    print("\n=== 发布系统错误 ===")
    publisher.publish(broker, "system.errors", {"type": "error", "message": "数据库连接失败", "level": "critical"})
    
    print(f"\n=== 统计信息 ===")
    print(f"消息总数: {broker.message_count}")
    print(f"发布者发布数: {publisher.published_count}")
    print(f"主题列表: {broker.get_topics()}")
    
    print("\n=== 使用PubSubClient ===")
    client1 = PubSubClient("客户端1", broker)
    client2 = PubSubClient("客户端2", broker)
    
    client1.subscribe("chat")
    client2.subscribe("chat")
    
    client1.publish("chat", "大家好！")
    client2.publish("chat", "你好！")
    
    print(f"客户端1收到消息: {len(client1.get_messages())}")
    print(f"客户端2收到消息: {len(client2.get_messages())}")


if __name__ == "__main__":
    main()
