# -----------------------------
# 题目：实现分布式事件溯源系统。
# 描述：支持事件存储、事件重放、状态重建。
# -----------------------------

import time
import threading
import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from collections import defaultdict

class EventType(Enum):
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    CUSTOM = "custom"

@dataclass
class Event:
    event_id: str
    event_type: str
    aggregate_id: str
    aggregate_type: str
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    version: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'aggregate_id': self.aggregate_id,
            'aggregate_type': self.aggregate_type,
            'data': self.data,
            'metadata': self.metadata,
            'timestamp': self.timestamp,
            'datetime': datetime.fromtimestamp(self.timestamp).isoformat(),
            'version': self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        return cls(
            event_id=data['event_id'],
            event_type=data['event_type'],
            aggregate_id=data['aggregate_id'],
            aggregate_type=data['aggregate_type'],
            data=data['data'],
            metadata=data.get('metadata', {}),
            timestamp=data['timestamp'],
            version=data.get('version', 1)
        )

class EventStore:
    def __init__(self):
        self.events: List[Event] = []
        self._by_aggregate: Dict[str, List[int]] = defaultdict(list)
        self._by_type: Dict[str, List[int]] = defaultdict(list)
        self._event_counter = 0
        self._lock = threading.Lock()
    
    def append(self, event: Event) -> str:
        with self._lock:
            self._event_counter += 1
            if not event.event_id:
                event.event_id = f"evt-{int(time.time())}-{self._event_counter}"
            
            event.version = len(self._by_aggregate[event.aggregate_id]) + 1
            
            idx = len(self.events)
            self.events.append(event)
            
            self._by_aggregate[event.aggregate_id].append(idx)
            self._by_type[event.event_type].append(idx)
            
            return event.event_id
    
    def get_events(
        self,
        aggregate_id: str = None,
        event_type: str = None,
        from_version: int = None,
        to_version: int = None,
        from_timestamp: float = None,
        to_timestamp: float = None
    ) -> List[Event]:
        with self._lock:
            if aggregate_id:
                indices = self._by_aggregate.get(aggregate_id, [])
            elif event_type:
                indices = self._by_type.get(event_type, [])
            else:
                indices = range(len(self.events))
            
            result = []
            for idx in indices:
                event = self.events[idx]
                
                if from_version and event.version < from_version:
                    continue
                if to_version and event.version > to_version:
                    continue
                if from_timestamp and event.timestamp < from_timestamp:
                    continue
                if to_timestamp and event.timestamp > to_timestamp:
                    continue
                
                result.append(event)
            
            return result
    
    def get_all_events(self) -> List[Event]:
        with self._lock:
            return self.events.copy()

class Aggregate:
    def __init__(self, aggregate_id: str):
        self.aggregate_id = aggregate_id
        self.version = 0
        self._uncommitted_events: List[Event] = []
    
    def apply_event(self, event: Event):
        handler_name = f"on_{event.event_type}"
        handler = getattr(self, handler_name, None)
        if handler:
            handler(event)
        self.version = event.version
    
    def raise_event(self, event_type: str, data: Dict[str, Any], metadata: Dict = None):
        event = Event(
            event_id="",
            event_type=event_type,
            aggregate_id=self.aggregate_id,
            aggregate_type=self.__class__.__name__,
            data=data,
            metadata=metadata or {}
        )
        self._uncommitted_events.append(event)
        self.apply_event(event)
    
    def get_uncommitted_events(self) -> List[Event]:
        return self._uncommitted_events.copy()
    
    def mark_events_committed(self):
        self._uncommitted_events.clear()

class OrderAggregate(Aggregate):
    def __init__(self, aggregate_id: str):
        super().__init__(aggregate_id)
        self.status = "pending"
        self.items: List[Dict] = []
        self.total = 0
    
    def create(self, items: List[Dict]):
        self.raise_event("order_created", {"items": items})
    
    def add_item(self, item: Dict):
        self.raise_event("item_added", {"item": item})
    
    def remove_item(self, item_id: str):
        self.raise_event("item_removed", {"item_id": item_id})
    
    def complete(self):
        self.raise_event("order_completed", {})
    
    def cancel(self):
        self.raise_event("order_cancelled", {})
    
    def on_order_created(self, event: Event):
        self.items = event.data["items"]
        self.total = sum(item.get("price", 0) * item.get("quantity", 1) for item in self.items)
        self.status = "created"
    
    def on_item_added(self, event: Event):
        self.items.append(event.data["item"])
        item = event.data["item"]
        self.total += item.get("price", 0) * item.get("quantity", 1)
    
    def on_item_removed(self, event: Event):
        item_id = event.data["item_id"]
        for i, item in enumerate(self.items):
            if item.get("id") == item_id:
                self.total -= item.get("price", 0) * item.get("quantity", 1)
                self.items.pop(i)
                break
    
    def on_order_completed(self, event: Event):
        self.status = "completed"
    
    def on_order_cancelled(self, event: Event):
        self.status = "cancelled"

class EventSourcingRepository:
    def __init__(self, event_store: EventStore):
        self.event_store = event_store
    
    def save(self, aggregate: Aggregate):
        events = aggregate.get_uncommitted_events()
        for event in events:
            self.event_store.append(event)
        aggregate.mark_events_committed()
    
    def load(self, aggregate_id: str, aggregate_class: type) -> Optional[Aggregate]:
        aggregate = aggregate_class(aggregate_id)
        
        events = self.event_store.get_events(aggregate_id=aggregate_id)
        
        if not events:
            return None
        
        for event in events:
            aggregate.apply_event(event)
        
        return aggregate

class Projection:
    def __init__(self, name: str):
        self.name = name
        self._state: Dict[str, Any] = {}
        self._last_processed: Dict[str, int] = {}
    
    def apply(self, event: Event):
        handler_name = f"on_{event.event_type}"
        handler = getattr(self, handler_name, None)
        if handler:
            handler(event)
        self._last_processed[event.aggregate_id] = event.version
    
    def get_state(self) -> Dict[str, Any]:
        return self._state.copy()

class OrderSummaryProjection(Projection):
    def __init__(self):
        super().__init__("order_summary")
        self._state = {
            'total_orders': 0,
            'completed_orders': 0,
            'cancelled_orders': 0,
            'total_revenue': 0
        }
    
    def on_order_created(self, event: Event):
        self._state['total_orders'] += 1
    
    def on_order_completed(self, event: Event):
        self._state['completed_orders'] += 1
    
    def on_order_cancelled(self, event: Event):
        self._state['cancelled_orders'] += 1

class EventSourcingSystem:
    def __init__(self):
        self.event_store = EventStore()
        self.repository = EventSourcingRepository(self.event_store)
        self.projections: Dict[str, Projection] = {}
        self._lock = threading.Lock()
    
    def register_projection(self, projection: Projection):
        self.projections[projection.name] = projection
    
    def save_aggregate(self, aggregate: Aggregate):
        with self._lock:
            events = aggregate.get_uncommitted_events()
            self.repository.save(aggregate)
            
            for event in events:
                for projection in self.projections.values():
                    projection.apply(event)
    
    def load_aggregate(self, aggregate_id: str, aggregate_class: type) -> Optional[Aggregate]:
        return self.repository.load(aggregate_id, aggregate_class)
    
    def replay_events(self, from_timestamp: float = None):
        events = self.event_store.get_events(from_timestamp=from_timestamp)
        
        for event in events:
            for projection in self.projections.values():
                projection.apply(event)
    
    def get_events(self, aggregate_id: str = None) -> List[Event]:
        return self.event_store.get_events(aggregate_id=aggregate_id)

def main():
    system = EventSourcingSystem()
    
    projection = OrderSummaryProjection()
    system.register_projection(projection)
    
    order = OrderAggregate("order-001")
    order.create([
        {"id": "item-1", "name": "商品A", "price": 100, "quantity": 2}
    ])
    
    order.add_item({"id": "item-2", "name": "商品B", "price": 50, "quantity": 1})
    
    system.save_aggregate(order)
    
    print("订单状态:")
    print(f"  ID: {order.aggregate_id}")
    print(f"  版本: {order.version}")
    print(f"  状态: {order.status}")
    print(f"  商品: {order.items}")
    print(f"  总价: {order.total}")
    
    order.complete()
    system.save_aggregate(order)
    
    print("\n重建订单...")
    rebuilt = system.load_aggregate("order-001", OrderAggregate)
    if rebuilt:
        print(f"  状态: {rebuilt.status}")
        print(f"  版本: {rebuilt.version}")
    
    print("\n投影状态:")
    print(f"  {projection.get_state()}")
    
    print("\n事件历史:")
    events = system.get_events("order-001")
    for event in events:
        print(f"  [{event.version}] {event.event_type}: {event.data}")

if __name__ == "__main__":
    main()
