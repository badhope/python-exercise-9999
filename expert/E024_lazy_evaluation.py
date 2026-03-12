# -----------------------------
# 题目：实现惰性求值。
# -----------------------------

from typing import Any, Callable, TypeVar, Generic
from functools import wraps

T = TypeVar('T')

class Lazy(Generic[T]):
    def __init__(self, func: Callable[[], T]):
        self._func = func
        self._value: T = None
        self._evaluated = False
    
    def __call__(self) -> T:
        if not self._evaluated:
            self._value = self._func()
            self._evaluated = True
        return self._value
    
    def is_evaluated(self) -> bool:
        return self._evaluated
    
    def reset(self):
        self._evaluated = False
        self._value = None

def lazy(func: Callable[[], T]) -> Lazy[T]:
    return Lazy(func)

class LazyProperty:
    def __init__(self, func: Callable):
        self.func = func
        self.attr_name = None
    
    def __set_name__(self, owner, name):
        self.attr_name = f"_lazy_{name}"
    
    def __get__(self, obj, owner=None):
        if obj is None:
            return self
        
        if not hasattr(obj, self.attr_name):
            value = self.func(obj)
            setattr(obj, self.attr_name, value)
        
        return getattr(obj, self.attr_name)

class LazySequence:
    def __init__(self, func: Callable[[int], Any], length: int = None):
        self._func = func
        self._length = length
        self._cache = {}
    
    def __getitem__(self, index: int) -> Any:
        if index < 0:
            raise IndexError("不支持负索引")
        
        if index not in self._cache:
            self._cache[index] = self._func(index)
        
        return self._cache[index]
    
    def __iter__(self):
        index = 0
        while self._length is None or index < self._length:
            yield self[index]
            index += 1
    
    def take(self, n: int) -> list:
        return [self[i] for i in range(n)]

class LazyMap:
    def __init__(self, func: Callable, iterable):
        self._func = func
        self._iterable = iterable
        self._cache = []
        self._exhausted = False
        self._iterator = iter(iterable)
    
    def __iter__(self):
        index = 0
        while True:
            while index >= len(self._cache) and not self._exhausted:
                try:
                    value = next(self._iterator)
                    self._cache.append(self._func(value))
                except StopIteration:
                    self._exhausted = True
                    break
            
            if index < len(self._cache):
                yield self._cache[index]
                index += 1
            else:
                break
    
    def to_list(self) -> list:
        return list(self)

class LazyFilter:
    def __init__(self, predicate: Callable, iterable):
        self._predicate = predicate
        self._iterable = iterable
        self._cache = []
        self._exhausted = False
        self._iterator = iter(iterable)
    
    def __iter__(self):
        index = 0
        while True:
            while index >= len(self._cache) and not self._exhausted:
                try:
                    value = next(self._iterator)
                    if self._predicate(value):
                        self._cache.append(value)
                except StopIteration:
                    self._exhausted = True
                    break
            
            if index < len(self._cache):
                yield self._cache[index]
                index += 1
            else:
                break
    
    def to_list(self) -> list:
        return list(self)

class DataLoader:
    @LazyProperty
    def expensive_data(self):
        print("加载大量数据...")
        import time
        time.sleep(0.1)
        return [i * i for i in range(100)]
    
    @LazyProperty
    def config(self):
        print("加载配置...")
        return {'debug': True, 'timeout': 30}

def main():
    print("=== Lazy类 ===")
    lazy_value = Lazy(lambda: sum(range(1000000)))
    print(f"是否已求值: {lazy_value.is_evaluated()}")
    
    result = lazy_value()
    print(f"结果: {result}")
    print(f"是否已求值: {lazy_value.is_evaluated()}")
    
    print("\n=== LazyProperty ===")
    loader = DataLoader()
    print("创建DataLoader实例")
    
    print("\n第一次访问expensive_data:")
    data = loader.expensive_data[:5]
    print(f"数据: {data}")
    
    print("\n第二次访问expensive_data:")
    data = loader.expensive_data[:5]
    print(f"数据: {data}")
    
    print("\n=== LazySequence ===")
    fib = LazySequence(lambda n: n if n < 2 else fib[n-1] + fib[n-2], length=20)
    print(f"前10个斐波那契数: {fib.take(10)}")
    
    print("\n=== LazyMap ===")
    lazy_map = LazyMap(lambda x: x * x, range(10))
    print(f"前5个平方数: {list(lazy_map)[:5]}")
    
    print("\n=== LazyFilter ===")
    lazy_filter = LazyFilter(lambda x: x % 2 == 0, range(20))
    print(f"前5个偶数: {lazy_filter.to_list()[:5]}")


if __name__ == "__main__":
    main()
