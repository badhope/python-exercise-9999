# -----------------------------
# 题目：实现函数组合。
# -----------------------------

from typing import Callable, TypeVar, Any, List
from functools import reduce, wraps

T = TypeVar('T')
U = TypeVar('U')

class Compose:
    def __init__(self, *functions: Callable):
        self.functions = list(functions)
    
    def __call__(self, value: Any) -> Any:
        return reduce(lambda v, f: f(v), reversed(self.functions), value)
    
    def __or__(self, other: Callable) -> 'Compose':
        return Compose(*self.functions, other)
    
    def __ror__(self, other: Callable) -> 'Compose':
        return Compose(other, *self.functions)
    
    def add(self, func: Callable) -> 'Compose':
        self.functions.append(func)
        return self

def compose(*functions: Callable) -> Callable:
    def composed(value: Any) -> Any:
        return reduce(lambda v, f: f(v), reversed(functions), value)
    return composed

def pipe(*functions: Callable) -> Callable:
    def piped(value: Any) -> Any:
        return reduce(lambda v, f: f(v), functions, value)
    return piped

class Pipeline:
    def __init__(self, value: Any = None):
        self._value = value
        self._functions: List[Callable] = []
    
    def apply(self, func: Callable) -> 'Pipeline':
        self._functions.append(func)
        return self
    
    def map(self, func: Callable) -> 'Pipeline':
        return self.apply(lambda x: [func(i) for i in x])
    
    def filter(self, predicate: Callable) -> 'Pipeline':
        return self.apply(lambda x: [i for i in x if predicate(i)])
    
    def reduce(self, func: Callable, initial: Any = None) -> 'Pipeline':
        def reducer(x):
            if initial is not None:
                return reduce(func, x, initial)
            return reduce(func, x)
        return self.apply(reducer)
    
    def execute(self) -> Any:
        result = self._value
        for func in self._functions:
            result = func(result)
        return result

class Curry:
    def __init__(self, func: Callable, arity: int = None):
        self.func = func
        self.arity = arity or len(func.__code__.co_varnames) - 1
        self.args = []
    
    def __call__(self, *args) -> Any:
        new_args = self.args + list(args)
        
        if len(new_args) >= self.arity:
            return self.func(*new_args[:self.arity])
        
        new_curry = Curry(self.func, self.arity)
        new_curry.args = new_args
        return new_curry

def curry(func: Callable) -> Curry:
    return Curry(func)

def memoize(func: Callable) -> Callable:
    cache = {}
    
    @wraps(func)
    def wrapped(*args):
        key = str(args)
        if key not in cache:
            cache[key] = func(*args)
        return cache[key]
    
    return wrapped

def partial(func: Callable, *fixed_args) -> Callable:
    @wraps(func)
    def wrapped(*args):
        return func(*fixed_args, *args)
    return wrapped

def main():
    print("=== compose函数 ===")
    add_one = lambda x: x + 1
    double = lambda x: x * 2
    square = lambda x: x ** 2
    
    composed = compose(square, double, add_one)
    print(f"compose(square, double, add_one)(3) = {composed(3)}")
    
    print("\n=== pipe函数 ===")
    piped = pipe(add_one, double, square)
    print(f"pipe(add_one, double, square)(3) = {piped(3)}")
    
    print("\n=== Compose类 ===")
    c = Compose(add_one, double)
    result = c(5)
    print(f"Compose(add_one, double)(5) = {result}")
    
    print("\n=== Pipeline类 ===")
    result = (Pipeline(range(10))
              .filter(lambda x: x % 2 == 0)
              .map(lambda x: x * x)
              .reduce(lambda a, b: a + b, 0)
              .execute())
    print(f"Pipeline结果: {result}")
    
    print("\n=== curry函数 ===")
    @curry
    def add(a, b, c):
        return a + b + c
    
    print(f"add(1)(2)(3) = {add(1)(2)(3)}")
    print(f"add(1, 2)(3) = {add(1, 2)(3)}")
    
    print("\n=== memoize函数 ===")
    @memoize
    def fibonacci(n):
        if n < 2:
            return n
        return fibonacci(n - 1) + fibonacci(n - 2)
    
    print(f"fibonacci(20) = {fibonacci(20)}")
    
    print("\n=== partial函数 ===")
    def power(base, exp):
        return base ** exp
    
    square = partial(power, 2)
    print(f"square(5) = {square(5)}")


if __name__ == "__main__":
    main()
