# -----------------------------
# 题目：实现生成器管道。
# -----------------------------

from typing import Generator, Callable, Any, Iterable, List
from functools import wraps

def generator_pipeline(*funcs: Callable):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            gen = func(*args, **kwargs)
            for f in funcs:
                gen = f(gen)
            return gen
        return wrapper
    return decorator

class Pipeline:
    def __init__(self, source: Iterable = None):
        self._source = source
        self._operations: List[Callable] = []
    
    def from_iterable(self, iterable: Iterable) -> 'Pipeline':
        self._source = iterable
        return self
    
    def map(self, func: Callable) -> 'Pipeline':
        def operation(gen):
            for item in gen:
                yield func(item)
        self._operations.append(operation)
        return self
    
    def filter(self, predicate: Callable) -> 'Pipeline':
        def operation(gen):
            for item in gen:
                if predicate(item):
                    yield item
        self._operations.append(operation)
        return self
    
    def take(self, n: int) -> 'Pipeline':
        def operation(gen):
            count = 0
            for item in gen:
                if count >= n:
                    break
                yield item
                count += 1
        self._operations.append(operation)
        return self
    
    def skip(self, n: int) -> 'Pipeline':
        def operation(gen):
            count = 0
            for item in gen:
                if count >= n:
                    yield item
                count += 1
        self._operations.append(operation)
        return self
    
    def distinct(self) -> 'Pipeline':
        def operation(gen):
            seen = set()
            for item in gen:
                if item not in seen:
                    seen.add(item)
                    yield item
        self._operations.append(operation)
        return self
    
    def flat_map(self, func: Callable) -> 'Pipeline':
        def operation(gen):
            for item in gen:
                for sub_item in func(item):
                    yield sub_item
        self._operations.append(operation)
        return self
    
    def group_by(self, key_func: Callable) -> 'Pipeline':
        def operation(gen):
            groups = {}
            for item in gen:
                key = key_func(item)
                if key not in groups:
                    groups[key] = []
                groups[key].append(item)
            for key, items in groups.items():
                yield (key, items)
        self._operations.append(operation)
        return self
    
    def sort(self, key: Callable = None, reverse: bool = False) -> 'Pipeline':
        def operation(gen):
            for item in sorted(gen, key=key, reverse=reverse):
                yield item
        self._operations.append(operation)
        return self
    
    def batch(self, size: int) -> 'Pipeline':
        def operation(gen):
            batch = []
            for item in gen:
                batch.append(item)
                if len(batch) >= size:
                    yield batch
                    batch = []
            if batch:
                yield batch
        self._operations.append(operation)
        return self
    
    def execute(self) -> Generator:
        gen = iter(self._source)
        for operation in self._operations:
            gen = operation(gen)
        return gen
    
    def to_list(self) -> List:
        return list(self.execute())
    
    def first(self, default: Any = None) -> Any:
        for item in self.execute():
            return item
        return default
    
    def count(self) -> int:
        return sum(1 for _ in self.execute())
    
    def sum(self) -> Any:
        return sum(self.execute())
    
    def reduce(self, func: Callable, initial: Any = None) -> Any:
        gen = self.execute()
        if initial is not None:
            result = initial
        else:
            result = next(gen)
        
        for item in gen:
            result = func(result, item)
        
        return result

def fibonacci_generator(n: int) -> Generator[int, None, None]:
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

def prime_generator(limit: int) -> Generator[int, None, None]:
    def is_prime(n):
        if n < 2:
            return False
        for i in range(2, int(n ** 0.5) + 1):
            if n % i == 0:
                return False
        return True
    
    for i in range(2, limit):
        if is_prime(i):
            yield i

def file_lines_generator(filepath: str) -> Generator[str, None, None]:
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            yield line.strip()

def main():
    print("=== Pipeline基本操作 ===")
    result = (Pipeline(range(20))
              .filter(lambda x: x % 2 == 0)
              .map(lambda x: x * x)
              .take(5)
              .to_list())
    print(f"结果: {result}")
    
    print("\n=== 分组操作 ===")
    result = (Pipeline(['apple', 'banana', 'cherry', 'apricot', 'blueberry'])
              .group_by(lambda x: x[0])
              .to_list())
    for key, items in result:
        print(f"  {key}: {items}")
    
    print("\n=== 批处理 ===")
    result = (Pipeline(range(10))
              .batch(3)
              .to_list())
    print(f"批处理结果: {result}")
    
    print("\n=== 斐波那契生成器 ===")
    result = (Pipeline(fibonacci_generator(15))
              .filter(lambda x: x % 2 == 0)
              .take(5)
              .to_list())
    print(f"偶数斐波那契数: {result}")
    
    print("\n=== 素数生成器 ===")
    result = (Pipeline(prime_generator(50))
              .take(10)
              .to_list())
    print(f"前10个素数: {result}")
    
    print("\n=== 统计操作 ===")
    count = (Pipeline(range(100))
             .filter(lambda x: x % 3 == 0)
             .count())
    print(f"100以内3的倍数个数: {count}")


if __name__ == "__main__":
    main()
