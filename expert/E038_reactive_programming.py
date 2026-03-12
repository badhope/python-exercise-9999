# -----------------------------
# 题目：实现响应式编程。
# -----------------------------

from typing import Callable, Any, List, Optional, TypeVar
from dataclasses import dataclass
from threading import Lock
import time

T = TypeVar('T')

@dataclass
class Subscription:
    id: int
    observer: 'Observer'

class Observer:
    def on_next(self, value: Any):
        pass
    
    def on_error(self, error: Exception):
        pass
    
    def on_complete(self):
        pass

class Observable:
    def __init__(self, subscribe_func: Callable = None):
        self._subscribe_func = subscribe_func
        self._next_id = 0
        self._lock = Lock()
    
    def subscribe(self, 
                  on_next: Callable = None, 
                  on_error: Callable = None, 
                  on_complete: Callable = None) -> Subscription:
        
        class SimpleObserver(Observer):
            def __init__(self, n, e, c):
                self._on_next = n
                self._on_error = e
                self._on_complete = c
            
            def on_next(self, value):
                if self._on_next:
                    self._on_next(value)
            
            def on_error(self, error):
                if self._on_error:
                    self._on_error(error)
            
            def on_complete(self):
                if self._on_complete:
                    self._on_complete()
        
        observer = SimpleObserver(on_next, on_error, on_complete)
        
        with self._lock:
            sub_id = self._next_id
            self._next_id += 1
        
        if self._subscribe_func:
            self._subscribe_func(observer)
        
        return Subscription(sub_id, observer)
    
    def map(self, func: Callable) -> 'Observable':
        def subscribe(observer: Observer):
            def on_next(value):
                observer.on_next(func(value))
            
            self.subscribe(on_next, observer.on_error, observer.on_complete)
        
        return Observable(subscribe)
    
    def filter(self, predicate: Callable) -> 'Observable':
        def subscribe(observer: Observer):
            def on_next(value):
                if predicate(value):
                    observer.on_next(value)
            
            self.subscribe(on_next, observer.on_error, observer.on_complete)
        
        return Observable(subscribe)
    
    def take(self, count: int) -> 'Observable':
        def subscribe(observer: Observer):
            taken = [0]
            
            def on_next(value):
                if taken[0] < count:
                    observer.on_next(value)
                    taken[0] += 1
                    if taken[0] >= count:
                        observer.on_complete()
            
            self.subscribe(on_next, observer.on_error, observer.on_complete)
        
        return Observable(subscribe)
    
    def debounce(self, milliseconds: int) -> 'Observable':
        def subscribe(observer: Observer):
            last_time = [0]
            
            def on_next(value):
                now = time.time() * 1000
                if now - last_time[0] >= milliseconds:
                    observer.on_next(value)
                    last_time[0] = now
            
            self.subscribe(on_next, observer.on_error, observer.on_complete)
        
        return Observable(subscribe)
    
    def distinct_until_changed(self) -> 'Observable':
        def subscribe(observer: Observer):
            last_value = [None]
            first = [True]
            
            def on_next(value):
                if first[0] or value != last_value[0]:
                    observer.on_next(value)
                    last_value[0] = value
                    first[0] = False
            
            self.subscribe(on_next, observer.on_error, observer.on_complete)
        
        return Observable(subscribe)
    
    def merge(self, other: 'Observable') -> 'Observable':
        def subscribe(observer: Observer):
            self.subscribe(observer.on_next, observer.on_error, observer.on_complete)
            other.subscribe(observer.on_next, observer.on_error, observer.on_complete)
        
        return Observable(subscribe)

class Subject(Observable, Observer):
    def __init__(self):
        super().__init__()
        self._observers: List[Observer] = []
        self._lock = Lock()
    
    def on_next(self, value: Any):
        with self._lock:
            observers = self._observers.copy()
        
        for observer in observers:
            observer.on_next(value)
    
    def on_error(self, error: Exception):
        with self._lock:
            observers = self._observers.copy()
        
        for observer in observers:
            observer.on_error(error)
    
    def on_complete(self):
        with self._lock:
            observers = self._observers.copy()
        
        for observer in observers:
            observer.on_complete()
    
    def subscribe(self, on_next: Callable = None, on_error: Callable = None, 
                  on_complete: Callable = None) -> Subscription:
        
        subscription = super().subscribe(on_next, on_error, on_complete)
        
        with self._lock:
            self._observers.append(subscription.observer)
        
        return subscription

class BehaviorSubject(Subject):
    def __init__(self, initial_value: Any):
        super().__init__()
        self._value = initial_value
    
    def on_next(self, value: Any):
        self._value = value
        super().on_next(value)
    
    def subscribe(self, on_next: Callable = None, on_error: Callable = None, 
                  on_complete: Callable = None) -> Subscription:
        subscription = super().subscribe(on_next, on_error, on_complete)
        
        if on_next and self._value is not None:
            on_next(self._value)
        
        return subscription
    
    @property
    def value(self) -> Any:
        return self._value

class ReplaySubject(Subject):
    def __init__(self, buffer_size: int = 10):
        super().__init__()
        self._buffer: List[Any] = []
        self._buffer_size = buffer_size
    
    def on_next(self, value: Any):
        self._buffer.append(value)
        if len(self._buffer) > self._buffer_size:
            self._buffer.pop(0)
        super().on_next(value)
    
    def subscribe(self, on_next: Callable = None, on_error: Callable = None, 
                  on_complete: Callable = None) -> Subscription:
        subscription = super().subscribe(on_next, on_error, on_complete)
        
        if on_next:
            for value in self._buffer:
                on_next(value)
        
        return subscription

def from_iterable(iterable) -> Observable:
    def subscribe(observer: Observer):
        for item in iterable:
            observer.on_next(item)
        observer.on_complete()
    
    return Observable(subscribe)

def interval(milliseconds: int) -> Observable:
    def subscribe(observer: Observer):
        import threading
        count = [0]
        running = [True]
        
        def tick():
            while running[0]:
                observer.on_next(count[0])
                count[0] += 1
                time.sleep(milliseconds / 1000)
        
        thread = threading.Thread(target=tick, daemon=True)
        thread.start()
    
    return Observable(subscribe)

def main():
    print("=== Observable基本操作 ===")
    
    values = []
    from_iterable([1, 2, 3, 4, 5]) \
        .filter(lambda x: x % 2 == 0) \
        .map(lambda x: x * x) \
        .subscribe(on_next=lambda v: values.append(v))
    
    print(f"过滤并映射: {values}")
    
    print("\n=== take操作符 ===")
    values = []
    from_iterable(range(10)) \
        .take(3) \
        .subscribe(on_next=lambda v: values.append(v))
    
    print(f"取前3个: {values}")
    
    print("\n=== Subject ===")
    subject = Subject()
    
    subject.subscribe(on_next=lambda v: print(f"观察者1: {v}"))
    subject.subscribe(on_next=lambda v: print(f"观察者2: {v}"))
    
    subject.on_next("Hello")
    subject.on_next("World")
    
    print("\n=== BehaviorSubject ===")
    behavior = BehaviorSubject("初始值")
    
    behavior.subscribe(on_next=lambda v: print(f"订阅者: {v}"))
    
    behavior.on_next("新值1")
    behavior.on_next("新值2")
    
    print(f"当前值: {behavior.value}")
    
    print("\n=== ReplaySubject ===")
    replay = ReplaySubject(buffer_size=3)
    
    replay.on_next("A")
    replay.on_next("B")
    replay.on_next("C")
    
    print("新订阅者将收到最近3个值:")
    replay.subscribe(on_next=lambda v: print(f"  收到: {v}"))


if __name__ == "__main__":
    main()
