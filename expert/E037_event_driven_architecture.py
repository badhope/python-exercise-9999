# -----------------------------
# 题目：实现事件驱动架构。
# -----------------------------

from typing import Callable, Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from threading import Lock
import queue
import threading

@dataclass
class Event:
    name: str
    data: Any
    timestamp: datetime
    source: str = None

class EventEmitter:
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}
        self._once_listeners: Dict[str, List[Callable]] = {}
        self._lock = Lock()
    
    def on(self, event_name: str, listener: Callable) -> 'EventEmitter':
        with self._lock:
            if event_name not in self._listeners:
                self._listeners[event_name] = []
            self._listeners[event_name].append(listener)
        return self
    
    def once(self, event_name: str, listener: Callable) -> 'EventEmitter':
        with self._lock:
            if event_name not in self._once_listeners:
                self._once_listeners[event_name] = []
            self._once_listeners[event_name].append(listener)
        return self
    
    def off(self, event_name: str, listener: Callable) -> 'EventEmitter':
        with self._lock:
            if event_name in self._listeners:
                self._listeners[event_name].remove(listener)
            if event_name in self._once_listeners:
                self._once_listeners[event_name].remove(listener)
        return self
    
    def emit(self, event_name: str, data: Any = None) -> bool:
        event = Event(
            name=event_name,
            data=data,
            timestamp=datetime.now()
        )
        
        with self._lock:
            listeners = self._listeners.get(event_name, []).copy()
            once_listeners = self._once_listeners.get(event_name, []).copy()
            
            if event_name in self._once_listeners:
                del self._once_listeners[event_name]
        
        for listener in listeners + once_listeners:
            try:
                listener(event)
            except Exception as e:
                print(f"事件处理器错误: {e}")
        
        return len(listeners + once_listeners) > 0

class EventBus:
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._emitter = EventEmitter()
                    cls._instance._event_queue = queue.Queue()
                    cls._instance._running = False
        return cls._instance
    
    def subscribe(self, event_name: str, handler: Callable):
        self._emitter.on(event_name, handler)
    
    def unsubscribe(self, event_name: str, handler: Callable):
        self._emitter.off(event_name, handler)
    
    def publish(self, event_name: str, data: Any = None):
        self._event_queue.put((event_name, data))
    
    def publish_sync(self, event_name: str, data: Any = None):
        self._emitter.emit(event_name, data)
    
    def start(self):
        self._running = True
        thread = threading.Thread(target=self._process_events, daemon=True)
        thread.start()
    
    def stop(self):
        self._running = False
    
    def _process_events(self):
        while self._running:
            try:
                event_name, data = self._event_queue.get(timeout=1)
                self._emitter.emit(event_name, data)
            except queue.Empty:
                continue

class EventHandler:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
    
    def handle(self, event: Event):
        pass

class EventSourcing:
    def __init__(self):
        self._events: List[Event] = []
        self._lock = Lock()
    
    def append(self, event: Event):
        with self._lock:
            self._events.append(event)
    
    def get_events(self, event_name: str = None, after: datetime = None) -> List[Event]:
        with self._lock:
            events = self._events.copy()
        
        if event_name:
            events = [e for e in events if e.name == event_name]
        
        if after:
            events = [e for e in events if e.timestamp > after]
        
        return events
    
    def replay(self, handler: Callable, event_name: str = None):
        events = self.get_events(event_name)
        for event in events:
            handler(event)

class Aggregate:
    def __init__(self):
        self._uncommitted_events: List[Event] = []
    
    def apply_event(self, event: Event):
        method_name = f"apply_{event.name}"
        method = getattr(self, method_name, None)
        if method:
            method(event.data)
    
    def raise_event(self, name: str, data: Any):
        event = Event(
            name=name,
            data=data,
            timestamp=datetime.now()
        )
        self._uncommitted_events.append(event)
        self.apply_event(event)
    
    def get_uncommitted_events(self) -> List[Event]:
        return self._uncommitted_events.copy()
    
    def mark_committed(self):
        self._uncommitted_events.clear()

class Order(Aggregate):
    def __init__(self):
        super().__init__()
        self.id = None
        self.items = []
        self.status = None
    
    def create(self, order_id: str, items: List[dict]):
        self.raise_event('order_created', {
            'id': order_id,
            'items': items
        })
    
    def add_item(self, item: dict):
        if self.status != 'created':
            raise ValueError("订单状态不允许添加商品")
        self.raise_event('item_added', item)
    
    def submit(self):
        if not self.items:
            raise ValueError("订单为空")
        self.raise_event('order_submitted', {})
    
    def apply_order_created(self, data: dict):
        self.id = data['id']
        self.items = data['items']
        self.status = 'created'
    
    def apply_item_added(self, data: dict):
        self.items.append(data)
    
    def apply_order_submitted(self, data: dict):
        self.status = 'submitted'

def main():
    print("=== EventEmitter ===")
    emitter = EventEmitter()
    
    def on_message(event: Event):
        print(f"收到消息: {event.data}")
    
    emitter.on('message', on_message)
    emitter.emit('message', 'Hello World!')
    
    print("\n=== EventBus ===")
    bus = EventBus()
    
    def handle_order(event: Event):
        print(f"处理订单: {event.data}")
    
    bus.subscribe('order_created', handle_order)
    bus.publish_sync('order_created', {'order_id': 'ORD-001'})
    
    print("\n=== EventSourcing ===")
    store = EventSourcing()
    
    store.append(Event('user_created', {'id': 1, 'name': '张三'}, datetime.now()))
    store.append(Event('user_updated', {'id': 1, 'name': '李四'}, datetime.now()))
    
    events = store.get_events()
    print(f"事件数量: {len(events)}")
    
    print("\n=== Order聚合 ===")
    order = Order()
    order.create('ORD-001', [{'name': '商品A', 'price': 100}])
    order.add_item({'name': '商品B', 'price': 200})
    order.submit()
    
    print(f"订单ID: {order.id}")
    print(f"订单状态: {order.status}")
    print(f"商品数量: {len(order.items)}")
    print(f"未提交事件: {len(order.get_uncommitted_events())}")


if __name__ == "__main__":
    main()
