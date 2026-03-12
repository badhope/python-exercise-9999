# -----------------------------
# 题目：实现装饰器模式高级版。
# -----------------------------

from typing import Callable, Any, List, Dict
from functools import wraps
import time

class DecoratorRegistry:
    _registry: Dict[str, Callable] = {}
    
    @classmethod
    def register(cls, name: str):
        def decorator(func: Callable):
            cls._registry[name] = func
            return func
        return decorator
    
    @classmethod
    def get(cls, name: str) -> Callable:
        return cls._registry.get(name)
    
    @classmethod
    def apply(cls, name: str, func: Callable) -> Callable:
        decorator = cls.get(name)
        if decorator:
            return decorator(func)
        return func

@DecoratorRegistry.register('timer')
def timer(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} 执行时间: {end - start:.4f}秒")
        return result
    return wrapper

@DecoratorRegistry.register('retry')
def retry(max_attempts: int = 3, delay: float = 1.0):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator

@DecoratorRegistry.register('memoize')
def memoize(func: Callable) -> Callable:
    cache: Dict[str, Any] = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    wrapper.cache = cache
    return wrapper

class ClassDecorator:
    def __call__(self, cls):
        for name, method in cls.__dict__.items():
            if callable(method) and not name.startswith('_'):
                setattr(cls, name, self._decorate_method(method))
        return cls
    
    def _decorate_method(self, method: Callable) -> Callable:
        @wraps(method)
        def wrapper(*args, **kwargs):
            print(f"调用方法: {method.__name__}")
            return method(*args, **kwargs)
        return wrapper

def log_calls(level: str = 'INFO'):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(f"[{level}] 调用 {func.__name__}")
            result = func(*args, **kwargs)
            print(f"[{level}] 返回 {func.__name__}")
            return result
        return wrapper
    return decorator

def validate_types(**types):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            import inspect
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            
            for name, value in bound.arguments.items():
                if name in types and not isinstance(value, types[name]):
                    raise TypeError(f"参数 {name} 期望类型 {types[name]}, 实际类型 {type(value)}")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def deprecated(message: str = None):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            import warnings
            msg = message or f"函数 {func.__name__} 已弃用"
            warnings.warn(msg, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)
        return wrapper
    return decorator

def singleton(cls):
    instances = {}
    
    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    get_instance.__cls__ = cls
    return get_instance

def main():
    print("=== 注册装饰器 ===")
    
    @DecoratorRegistry.apply('timer')
    def slow_function():
        time.sleep(0.1)
        return "完成"
    
    result = slow_function()
    print(f"结果: {result}")
    
    print("\n=== 重试装饰器 ===")
    
    @DecoratorRegistry.get('retry')(max_attempts=3)
    def unstable_function():
        import random
        if random.random() < 0.7:
            raise Exception("随机失败")
        return "成功"
    
    try:
        result = unstable_function()
        print(f"结果: {result}")
    except Exception as e:
        print(f"失败: {e}")
    
    print("\n=== 类型验证装饰器 ===")
    
    @validate_types(name=str, age=int)
    def greet(name, age):
        return f"{name} 今年 {age} 岁"
    
    print(greet("张三", 25))
    
    try:
        greet("张三", "二十五")
    except TypeError as e:
        print(f"错误: {e}")
    
    print("\n=== 单例装饰器 ===")
    
    @singleton
    class Config:
        def __init__(self):
            self.debug = False
    
    c1 = Config()
    c2 = Config()
    print(f"c1 is c2: {c1 is c2}")


if __name__ == "__main__":
    main()
