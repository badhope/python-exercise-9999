# -----------------------------
# 题目：实现事件总线。
# 描述：支持事件发布订阅、异步处理、事件过滤。
# -----------------------------

import time
import threading
import uuid
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
from queue import Queue
from collections import defaultdict

class EventPriority(Enum):
    LOW = 1
    NORMAL = 5
    HIGH = 10
    CRITICAL = 20

@dataclass
class Event:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    event_type: str = ""
    source: str = ""
    data: Any = None
    timestamp: float = field(default_factory=time.time)
    priority: EventPriority = EventPriority.NORMAL
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Subscription:
    subscription_id: str
    event_type: str
    handler: Callable[[Event], None]
    filter_func: Optional[Callable[[Event], bool]] = None
    priority: int = 0
    active: bool = True

class EventHandler:
    def __init__(self, handler: Callable, filter_func: Callable = None, priority: int = 0):
        self.handler = handler
        self.filter_func = filter_func
        self.priority = priority

class EventBus:
    def __init__(self, async_mode: bool = True, max_workers: int = 4):
        self._handlers: Dict[str, List[EventHandler]] = defaultdict(list)
        self._subscriptions: Dict[str, Subscription] = {}
        self._event_queue: Queue = Queue()
        self._async_mode = async_mode
        self._max_workers = max_workers
        self._running = False
        self._workers: List[threading.Thread] = []
        self._lock = threading.RLock()
        self._event_history: List[Event] = []
        self._max_history = 1000
    
    def subscribe(
        self,
        event_type: str,
        handler: Callable[[Event], None],
        filter_func: Callable[[Event], bool] = None,
        priority: int = 0
    ) -> str:
        subscription_id = str(uuid.uuid4())[:8]
        
        with self._lock:
            event_handler = EventHandler(handler, filter_func, priority)
            self._handlers[event_type].append(event_handler)
            self._handlers[event_type].sort(key=lambda h: h.priority, reverse=True)
            
            self._subscriptions[subscription_id] = Subscription(
                subscription_id=subscription_id,
                event_type=event_type,
                handler=handler,
                filter_func=filter_func,
                priority=priority
            )
        
        return subscription_id
    
    def unsubscribe(self, subscription_id: str) -> bool:
        with self._lock:
            subscription = self._subscriptions.pop(subscription_id, None)
            if subscription:
                handlers = self._handlers.get(subscription.event_type, [])
                self._handlers[subscription.event_type] = [
                    h for h in handlers if h.handler != subscription.handler
                ]
                return True
            return False
    
    def publish(self, event: Event) -> str:
        if self._async_mode and self._running:
            self._event_queue.put(event)
        else:
            self._dispatch_event(event)
        
        with self._lock:
            self._event_history.append(event)
            if len(self._event_history) > self._max_history:
                self._event_history.pop(0)
        
        return event.event_id
    
    def publish_simple(self, event_type: str, data: Any = None) -> str:
        event = Event(event_type=event_type, data=data)
        return self.publish(event)
    
    def _dispatch_event(self, event: Event):
        handlers = self._handlers.get(event.event_type, [])
        wildcard_handlers = self._handlers.get('*', [])
        
        all_handlers = handlers + wildcard_handlers
        
        for handler in all_handlers:
            if handler.filter_func and not handler.filter_func(event):
                continue
            
            try:
                handler.handler(event)
            except Exception as e:
                print(f"事件处理错误: {e}")
    
    def start(self):
        if not self._async_mode:
            return
        
        self._running = True
        
        for i in range(self._max_workers):
            worker = threading.Thread(target=self._worker_loop, args=(i,))
            worker.daemon = True
            worker.start()
            self._workers.append(worker)
    
    def stop(self):
        self._running = False
        for worker in self._workers:
            worker.join(timeout=2.0)
        self._workers.clear()
    
    def _worker_loop(self, worker_id: int):
        while self._running:
            try:
                event = self._event_queue.get(timeout=1.0)
                self._dispatch_event(event)
            except:
                pass
    
    def get_history(self, event_type: str = None, limit: int = 100) -> List[Event]:
        events = self._event_history
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        return events[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            return {
                'subscriptions': len(self._subscriptions),
                'event_types': list(self._handlers.keys()),
                'history_size': len(self._event_history),
                'queue_size': self._event_queue.qsize()
            }

class EventAggregator:
    def __init__(self, event_bus: EventBus, window_size: float = 5.0):
        self.event_bus = event_bus
        self.window_size = window_size
        self._events: Dict[str, List[Event]] = defaultdict(list)
        self._aggregators: Dict[str, Callable] = {}
    
    def register_aggregator(
        self,
        event_type: str,
        aggregate_func: Callable[[List[Event]], Any],
        output_event_type: str
    ):
        self._aggregators[event_type] = {
            'func': aggregate_func,
            'output': output_event_type
        }
        
        self.event_bus.subscribe(
            event_type,
            lambda e: self._collect_event(e)
        )
    
    def _collect_event(self, event: Event):
        self._events[event.event_type].append(event)
        
        now = time.time()
        self._events[event.event_type] = [
            e for e in self._events[event.event_type]
            if now - e.timestamp <= self.window_size
        ]

def main():
    event_bus = EventBus(async_mode=False)
    
    received_events = []
    
    def order_handler(event: Event):
        print(f"订单事件: {event.event_type}, 数据: {event.data}")
        received_events.append(event)
    
    def payment_handler(event: Event):
        print(f"支付事件: {event.event_type}, 数据: {event.data}")
    
    def high_priority_handler(event: Event):
        print(f"[高优先级] 事件: {event.event_type}")
    
    sub1 = event_bus.subscribe("order.created", order_handler)
    sub2 = event_bus.subscribe("order.updated", order_handler)
    sub3 = event_bus.subscribe("payment.*", payment_handler)
    sub4 = event_bus.subscribe("*", high_priority_handler, priority=100)
    
    event_bus.publish_simple("order.created", {"order_id": "ORD-001", "amount": 100})
    event_bus.publish_simple("order.updated", {"order_id": "ORD-001", "status": "paid"})
    event_bus.publish_simple("payment.completed", {"payment_id": "PAY-001"})
    
    print(f"\n订阅数: {len(event_bus._subscriptions)}")
    print(f"事件历史: {len(event_bus.get_history())}")
    
    event_bus.unsubscribe(sub1)
    print(f"取消订阅后: {len(event_bus._subscriptions)}")

if __name__ == "__main__":
    main()
