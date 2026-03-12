# -----------------------------
# 题目：实现观察者模式高级版。
# -----------------------------

from typing import Dict, List, Any, Callable, Optional, TypeVar, Generic
from dataclasses import dataclass
from threading import Lock
from abc import ABC, abstractmethod
from datetime import datetime

T = TypeVar('T')

@dataclass
class Event:
    name: str
    data: Any
    timestamp: datetime
    source: str = None

class Observer(ABC, Generic[T]):
    @abstractmethod
    def on_next(self, value: T):
        pass
    
    def on_error(self, error: Exception):
        pass
    
    def on_complete(self):
        pass

class Subject(Generic[T]):
    def __init__(self):
        self._observers: List[Observer[T]] = []
        self._lock = Lock()
        self._completed = False
    
    def subscribe(self, observer: Observer[T]):
        with self._lock:
            self._observers.append(observer)
        return self
    
    def unsubscribe(self, observer: Observer[T]):
        with self._lock:
            if observer in self._observers:
                self._observers.remove(observer)
    
    def next(self, value: T):
        if self._completed:
            return
        
        with self._lock:
            observers = self._observers.copy()
        
        for observer in observers:
            try:
                observer.on_next(value)
            except Exception as e:
                observer.on_error(e)
    
    def error(self, error: Exception):
        with self._lock:
            observers = self._observers.copy()
        
        for observer in observers:
            observer.on_error(error)
    
    def complete(self):
        self._completed = True
        
        with self._lock:
            observers = self._observers.copy()
        
        for observer in observers:
            observer.on_complete()

class BehaviorSubject(Subject[T]):
    def __init__(self, initial_value: T = None):
        super().__init__()
        self._value = initial_value
    
    def next(self, value: T):
        self._value = value
        super().next(value)
    
    def subscribe(self, observer: Observer[T]):
        super().subscribe(observer)
        if self._value is not None:
            observer.on_next(self._value)
    
    @property
    def value(self) -> T:
        return self._value

class ReplaySubject(Subject[T]):
    def __init__(self, buffer_size: int = 10):
        super().__init__()
        self._buffer: List[T] = []
        self._buffer_size = buffer_size
    
    def next(self, value: T):
        self._buffer.append(value)
        if len(self._buffer) > self._buffer_size:
            self._buffer.pop(0)
        super().next(value)
    
    def subscribe(self, observer: Observer[T]):
        super().subscribe(observer)
        for value in self._buffer:
            observer.on_next(value)

class Observable(Generic[T]):
    def __init__(self, subscribe_func: Callable):
        self._subscribe_func = subscribe_func
    
    def subscribe(self, 
                  on_next: Callable[[T], None] = None,
                  on_error: Callable[[Exception], None] = None,
                  on_complete: Callable[[], None] = None) -> 'Subscription':
        
        class SimpleObserver(Observer[T]):
            def __init__(self):
                self._on_next = on_next
                self._on_error = on_error
                self._on_complete = on_complete
            
            def on_next(self, value: T):
                if self._on_next:
                    self._on_next(value)
            
            def on_error(self, error: Exception):
                if self._on_error:
                    self._on_error(error)
            
            def on_complete(self):
                if self._on_complete:
                    self._on_complete()
        
        observer = SimpleObserver()
        self._subscribe_func(observer)
        
        return Subscription(observer)
    
    def map(self, func: Callable[[T], Any]) -> 'Observable':
        def subscribe(observer: Observer):
            def on_next(value):
                observer.on_next(func(value))
            
            self.subscribe(on_next, observer.on_error, observer.on_complete)
        
        return Observable(subscribe)
    
    def filter(self, predicate: Callable[[T], bool]) -> 'Observable':
        def subscribe(observer: Observer):
            def on_next(value):
                if predicate(value):
                    observer.on_next(value)
            
            self.subscribe(on_next, observer.on_error, observer.on_complete)
        
        return Observable(subscribe)

class Subscription:
    def __init__(self, observer: Observer):
        self._observer = observer
    
    def unsubscribe(self):
        pass

class EventEmitter:
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}
        self._once_listeners: Dict[str, List[Callable]] = {}
        self._lock = Lock()
    
    def on(self, event: str, listener: Callable) -> 'EventEmitter':
        with self._lock:
            if event not in self._listeners:
                self._listeners[event] = []
            self._listeners[event].append(listener)
        return self
    
    def once(self, event: str, listener: Callable) -> 'EventEmitter':
        with self._lock:
            if event not in self._once_listeners:
                self._once_listeners[event] = []
            self._once_listeners[event].append(listener)
        return self
    
    def emit(self, event: str, data: Any = None) -> bool:
        e = Event(event, data, datetime.now())
        
        with self._lock:
            listeners = self._listeners.get(event, []).copy()
            once_listeners = self._once_listeners.get(event, []).copy()
            
            if event in self._once_listeners:
                del self._once_listeners[event]
        
        for listener in listeners + once_listeners:
            try:
                listener(e)
            except Exception as ex:
                print(f"监听器错误: {ex}")
        
        return len(listeners + once_listeners) > 0
    
    def off(self, event: str, listener: Callable) -> 'EventEmitter':
        with self._lock:
            if event in self._listeners and listener in self._listeners[event]:
                self._listeners[event].remove(listener)
        return self

def main():
    print("=== Subject ===")
    subject = Subject[int]()
    
    class PrintObserver(Observer[int]):
        def __init__(self, name: str):
            self.name = name
        
        def on_next(self, value: int):
            print(f"{self.name}: {value}")
    
    subject.subscribe(PrintObserver("观察者1"))
    subject.subscribe(PrintObserver("观察者2"))
    
    subject.next(1)
    subject.next(2)
    
    print("\n=== BehaviorSubject ===")
    behavior = BehaviorSubject[str]("初始值")
    
    behavior.subscribe(PrintObserver("订阅者1"))
    behavior.next("新值")
    behavior.subscribe(PrintObserver("订阅者2"))
    
    print(f"\n当前值: {behavior.value}")
    
    print("\n=== Observable操作符 ===")
    def create_observable(observer: Observer[int]):
        for i in range(5):
            observer.on_next(i)
        observer.on_complete()
    
    (Observable(create_observable)
     .filter(lambda x: x % 2 == 0)
     .map(lambda x: x * x)
     .subscribe(on_next=lambda v: print(f"结果: {v}")))
    
    print("\n=== EventEmitter ===")
    emitter = EventEmitter()
    
    emitter.on('message', lambda e: print(f"收到: {e.data}"))
    emitter.once('connect', lambda e: print(f"连接: {e.data}"))
    
    emitter.emit('message', 'Hello')
    emitter.emit('connect', '成功')
    emitter.emit('connect', '再次连接')


if __name__ == "__main__":
    main()
