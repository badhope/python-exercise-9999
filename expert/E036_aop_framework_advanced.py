# -----------------------------
# 题目：实现AOP框架高级版。
# -----------------------------

from typing import Callable, Any, List, Dict, Optional
from functools import wraps
import time

class Aspect:
    def before(self, *args, **kwargs):
        pass
    
    def after(self, result: Any):
        pass
    
    def after_throwing(self, exception: Exception):
        pass
    
    def around(self, func: Callable, *args, **kwargs) -> Any:
        return func(*args, **kwargs)

class LoggingAspect(Aspect):
    def before(self, *args, **kwargs):
        print(f"[BEFORE] 参数: args={args}, kwargs={kwargs}")
    
    def after(self, result: Any):
        print(f"[AFTER] 返回: {result}")
    
    def after_throwing(self, exception: Exception):
        print(f"[EXCEPTION] 异常: {exception}")

class TimingAspect(Aspect):
    def around(self, func: Callable, *args, **kwargs) -> Any:
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"[TIMING] {func.__name__} 耗时: {end - start:.4f}秒")
        return result

class CachingAspect(Aspect):
    def __init__(self):
        self._cache: Dict[str, Any] = {}
    
    def around(self, func: Callable, *args, **kwargs) -> Any:
        key = str(args) + str(kwargs)
        
        if key in self._cache:
            print(f"[CACHE] 命中缓存: {key}")
            return self._cache[key]
        
        result = func(*args, **kwargs)
        self._cache[key] = result
        print(f"[CACHE] 缓存结果: {key}")
        return result

class RetryAspect(Aspect):
    def __init__(self, max_attempts: int = 3, delay: float = 1.0):
        self.max_attempts = max_attempts
        self.delay = delay
    
    def around(self, func: Callable, *args, **kwargs) -> Any:
        last_exception = None
        
        for attempt in range(self.max_attempts):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_attempts - 1:
                    print(f"[RETRY] 第{attempt + 1}次失败，重试中...")
                    time.sleep(self.delay)
        
        raise last_exception

class AspectProxy:
    def __init__(self, target: Any):
        self._target = target
        self._aspects: List[Aspect] = []
    
    def add_aspect(self, aspect: Aspect):
        self._aspects.append(aspect)
        return self
    
    def __getattr__(self, name: str):
        attr = getattr(self._target, name)
        
        if callable(attr):
            @wraps(attr)
            def wrapped(*args, **kwargs):
                for aspect in self._aspects:
                    aspect.before(*args, **kwargs)
                
                try:
                    result = attr(*args, **kwargs)
                    for aspect in self._aspects:
                        aspect.after(result)
                    return result
                except Exception as e:
                    for aspect in self._aspects:
                        aspect.after_throwing(e)
                    raise
            
            return wrapped
        
        return attr

def aspect(*aspects: Aspect):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            for a in aspects:
                a.before(*args, **kwargs)
            
            try:
                result = func(*args, **kwargs)
                for a in aspects:
                    a.after(result)
                return result
            except Exception as e:
                for a in aspects:
                    a.after_throwing(e)
                raise
        
        return wrapper
    return decorator

def around(aspect: Aspect):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return aspect.around(func, *args, **kwargs)
        return wrapper
    return decorator

class AspectBuilder:
    def __init__(self):
        self._aspects: List[Aspect] = []
    
    def with_logging(self) -> 'AspectBuilder':
        self._aspects.append(LoggingAspect())
        return self
    
    def with_timing(self) -> 'AspectBuilder':
        self._aspects.append(TimingAspect())
        return self
    
    def with_caching(self) -> 'AspectBuilder':
        self._aspects.append(CachingAspect())
        return self
    
    def with_retry(self, max_attempts: int = 3) -> 'AspectBuilder':
        self._aspects.append(RetryAspect(max_attempts))
        return self
    
    def build(self) -> List[Aspect]:
        return self._aspects

class Pointcut:
    def __init__(self):
        self._patterns: List[str] = []
    
    def matches(self, method_name: str) -> bool:
        import fnmatch
        return any(fnmatch.fnmatch(method_name, p) for p in self._patterns)
    
    def add_pattern(self, pattern: str):
        self._patterns.append(pattern)
        return self

class AspectWeaver:
    def __init__(self):
        self._pointcuts: Dict[Pointcut, List[Aspect]] = {}
    
    def register(self, pointcut: Pointcut, *aspects: Aspect):
        self._pointcuts[pointcut] = list(aspects)
    
    def weave(self, target: Any) -> Any:
        proxy = AspectProxy(target)
        
        for pointcut, aspects in self._pointcuts.items():
            for name in dir(target):
                if pointcut.matches(name):
                    for aspect in aspects:
                        proxy.add_aspect(aspect)
        
        return proxy

def main():
    print("=== 使用装饰器 ===")
    
    @aspect(LoggingAspect(), TimingAspect())
    def compute(n: int) -> int:
        return sum(range(n))
    
    result = compute(100000)
    print(f"结果: {result}")
    
    print("\n=== 使用around装饰器 ===")
    
    @around(CachingAspect())
    def fibonacci(n: int) -> int:
        if n < 2:
            return n
        return fibonacci(n - 1) + fibonacci(n - 2)
    
    print("第一次调用:")
    print(f"fibonacci(10) = {fibonacci(10)}")
    
    print("\n=== 使用AspectBuilder ===")
    aspects = (AspectBuilder()
               .with_logging()
               .with_timing()
               .build())
    
    @aspect(*aspects)
    def process_data(data: str) -> str:
        return data.upper()
    
    process_data("hello world")
    
    print("\n=== 使用AspectProxy ===")
    class Calculator:
        def add(self, a: int, b: int) -> int:
            return a + b
        
        def multiply(self, a: int, b: int) -> int:
            return a * b
    
    proxy = (AspectProxy(Calculator())
             .add_aspect(LoggingAspect())
             .add_aspect(TimingAspect()))
    
    print(f"add(3, 5) = {proxy.add(3, 5)}")


if __name__ == "__main__":
    main()
