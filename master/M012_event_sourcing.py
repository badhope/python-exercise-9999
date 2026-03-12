# -----------------------------
# 题目：实现事件溯源框架。
# 描述：通过事件流重建状态，支持事件回放。
# -----------------------------

from datetime import datetime
from typing import List, Dict, Any, Callable
from dataclasses import dataclass, field
import json

@dataclass
class Event:
    event_type: str
    aggregate_id: str
    data: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    version: int = 1

class EventStore:
    def __init__(self):
        self.events: List[Event] = []
        self.subscribers: List[Callable[[Event], None]] = []
    
    def append(self, event: Event):
        self.events.append(event)
        for subscriber in self.subscribers:
            subscriber(event)
    
    def get_events(self, aggregate_id: str = None) -> List[Event]:
        if aggregate_id:
            return [e for e in self.events if e.aggregate_id == aggregate_id]
        return self.events.copy()
    
    def subscribe(self, subscriber: Callable[[Event], None]):
        self.subscribers.append(subscriber)

class AggregateRoot:
    def __init__(self, aggregate_id: str):
        self.aggregate_id = aggregate_id
        self.version = 0
        self._uncommitted_events: List[Event] = []
    
    def apply_event(self, event: Event):
        self._apply(event)
        self.version = event.version
    
    def _apply(self, event: Event):
        method_name = f"apply_{event.event_type}"
        if hasattr(self, method_name):
            getattr(self, method_name)(event)
    
    def raise_event(self, event_type: str, data: Dict[str, Any]):
        self.version += 1
        event = Event(
            event_type=event_type,
            aggregate_id=self.aggregate_id,
            data=data,
            version=self.version
        )
        self._apply(event)
        self._uncommitted_events.append(event)

class BankAccount(AggregateRoot):
    def __init__(self, aggregate_id: str):
        super().__init__(aggregate_id)
        self.balance = 0
    
    def apply_AccountCreated(self, event: Event):
        self.balance = 0
    
    def apply_MoneyDeposited(self, event: Event):
        self.balance += event.data['amount']
    
    def apply_MoneyWithdrawn(self, event: Event):
        self.balance -= event.data['amount']
    
    def create(self):
        self.raise_event('AccountCreated', {})
    
    def deposit(self, amount: float):
        if amount <= 0:
            raise ValueError("存款金额必须大于0")
        self.raise_event('MoneyDeposited', {'amount': amount})
    
    def withdraw(self, amount: float):
        if amount <= 0:
            raise ValueError("取款金额必须大于0")
        if self.balance < amount:
            raise ValueError("余额不足")
        self.raise_event('MoneyWithdrawn', {'amount': amount})

class EventSourcingRepository:
    def __init__(self, event_store: EventStore, aggregate_class):
        self.event_store = event_store
        self.aggregate_class = aggregate_class
    
    def save(self, aggregate: AggregateRoot):
        for event in aggregate._uncommitted_events:
            self.event_store.append(event)
        aggregate._uncommitted_events.clear()
    
    def load(self, aggregate_id: str) -> AggregateRoot:
        aggregate = self.aggregate_class(aggregate_id)
        events = self.event_store.get_events(aggregate_id)
        for event in sorted(events, key=lambda e: e.version):
            aggregate.apply_event(event)
        return aggregate

def main():
    event_store = EventStore()
    repository = EventSourcingRepository(event_store, BankAccount)
    
    account = BankAccount("acc-001")
    account.create()
    account.deposit(1000)
    account.withdraw(300)
    repository.save(account)
    
    loaded_account = repository.load("acc-001")
    print(f"账户余额: {loaded_account.balance}")
    print(f"事件数量: {len(event_store.get_events('acc-001'))}")

if __name__ == "__main__":
    main()
