# -----------------------------
# 题目：实现简单的事件溯源。
# -----------------------------

from typing import Dict, List, Any, Callable, Type
from dataclasses import dataclass, field
from datetime import datetime
import json

@dataclass
class Event:
    event_type: str
    aggregate_id: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    version: int = 1

class EventStore:
    def __init__(self):
        self._events: Dict[str, List[Event]] = {}
        self._subscribers: Dict[str, List[Callable]] = {}
    
    def append(self, event: Event):
        if event.aggregate_id not in self._events:
            self._events[event.aggregate_id] = []
        
        event.version = len(self._events[event.aggregate_id]) + 1
        self._events[event.aggregate_id].append(event)
        
        self._publish(event)
    
    def get_events(self, aggregate_id: str, from_version: int = 0) -> List[Event]:
        events = self._events.get(aggregate_id, [])
        return [e for e in events if e.version > from_version]
    
    def get_all_events(self) -> List[Event]:
        all_events = []
        for events in self._events.values():
            all_events.extend(events)
        return sorted(all_events, key=lambda e: e.timestamp)
    
    def subscribe(self, event_type: str, handler: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
    
    def _publish(self, event: Event):
        handlers = self._subscribers.get(event.event_type, [])
        for handler in handlers:
            handler(event)
        
        all_handlers = self._subscribers.get('*', [])
        for handler in all_handlers:
            handler(event)

class Aggregate:
    def __init__(self, aggregate_id: str):
        self.aggregate_id = aggregate_id
        self.version = 0
        self._uncommitted_events: List[Event] = []
    
    def apply_event(self, event: Event):
        method_name = f"apply_{event.event_type}"
        method = getattr(self, method_name, None)
        if method:
            method(event.data)
        self.version = event.version
    
    def raise_event(self, event_type: str, data: Dict[str, Any]):
        event = Event(
            event_type=event_type,
            aggregate_id=self.aggregate_id,
            data=data
        )
        self._uncommitted_events.append(event)
        self.apply_event(event)
    
    def get_uncommitted_events(self) -> List[Event]:
        return self._uncommitted_events.copy()
    
    def mark_events_committed(self):
        self._uncommitted_events.clear()

class Repository:
    def __init__(self, event_store: EventStore, aggregate_class: Type[Aggregate]):
        self.event_store = event_store
        self.aggregate_class = aggregate_class
    
    def get(self, aggregate_id: str) -> Aggregate:
        aggregate = self.aggregate_class(aggregate_id)
        events = self.event_store.get_events(aggregate_id)
        
        for event in events:
            aggregate.apply_event(event)
        
        return aggregate
    
    def save(self, aggregate: Aggregate):
        for event in aggregate.get_uncommitted_events():
            self.event_store.append(event)
        aggregate.mark_events_committed()

class BankAccount(Aggregate):
    def __init__(self, account_id: str):
        super().__init__(account_id)
        self.balance = 0
        self.owner = None
        self.is_active = False
    
    def create(self, owner: str, initial_balance: int = 0):
        if self.is_active:
            raise ValueError("账户已存在")
        self.raise_event('account_created', {
            'owner': owner,
            'initial_balance': initial_balance
        })
    
    def deposit(self, amount: int):
        if not self.is_active:
            raise ValueError("账户未激活")
        if amount <= 0:
            raise ValueError("存款金额必须大于0")
        self.raise_event('money_deposited', {'amount': amount})
    
    def withdraw(self, amount: int):
        if not self.is_active:
            raise ValueError("账户未激活")
        if amount <= 0:
            raise ValueError("取款金额必须大于0")
        if amount > self.balance:
            raise ValueError("余额不足")
        self.raise_event('money_withdrawn', {'amount': amount})
    
    def close(self):
        if not self.is_active:
            raise ValueError("账户未激活")
        self.raise_event('account_closed', {})
    
    def apply_account_created(self, data: Dict):
        self.owner = data['owner']
        self.balance = data['initial_balance']
        self.is_active = True
    
    def apply_money_deposited(self, data: Dict):
        self.balance += data['amount']
    
    def apply_money_withdrawn(self, data: Dict):
        self.balance -= data['amount']
    
    def apply_account_closed(self, data: Dict):
        self.is_active = False

def main():
    event_store = EventStore()
    
    event_store.subscribe('*', lambda e: print(f"[事件] {e.event_type}: {e.data}"))
    
    repository = Repository(event_store, BankAccount)
    
    print("=== 创建账户 ===")
    account = BankAccount("ACC-001")
    account.create("张三", 1000)
    repository.save(account)
    print(f"账户余额: {account.balance}")
    
    print("\n=== 存款 ===")
    account = repository.get("ACC-001")
    account.deposit(500)
    repository.save(account)
    print(f"账户余额: {account.balance}")
    
    print("\n=== 取款 ===")
    account = repository.get("ACC-001")
    account.withdraw(300)
    repository.save(account)
    print(f"账户余额: {account.balance}")
    
    print("\n=== 事件历史 ===")
    events = event_store.get_events("ACC-001")
    for event in events:
        print(f"  v{event.version}: {event.event_type} @ {event.timestamp}")


if __name__ == "__main__":
    main()
