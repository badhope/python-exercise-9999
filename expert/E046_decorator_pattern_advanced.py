# -----------------------------
# 题目：实现装饰器模式高级版。
# -----------------------------

from typing import Callable, Any, List, Dict, Optional
from functools import wraps
from dataclasses import dataclass

@dataclass
class Component:
    name: str
    
    def operation(self) -> str:
        return self.name

class Decorator:
    def __init__(self, component: Component):
        self._component = component
    
    def operation(self) -> str:
        return self._component.operation()

class BorderDecorator(Decorator):
    def __init__(self, component: Component, border_char: str = "*"):
        super().__init__(component)
        self.border_char = border_char
    
    def operation(self) -> str:
        content = self._component.operation()
        border = self.border_char * (len(content) + 4)
        return f"{border}\n{self.border_char} {content} {self.border_char}\n{border}"

class ColorDecorator(Decorator):
    COLORS = {
        'red': '\033[91m',
        'green': '\033[92m',
        'blue': '\033[94m',
        'reset': '\033[0m'
    }
    
    def __init__(self, component: Component, color: str = 'green'):
        super().__init__(component)
        self.color = color
    
    def operation(self) -> str:
        content = self._component.operation()
        color_code = self.COLORS.get(self.color, '')
        reset_code = self.COLORS['reset']
        return f"{color_code}{content}{reset_code}"

class UpperCaseDecorator(Decorator):
    def operation(self) -> str:
        return self._component.operation().upper()

class PrefixDecorator(Decorator):
    def __init__(self, component: Component, prefix: str):
        super().__init__(component)
        self.prefix = prefix
    
    def operation(self) -> str:
        return f"{self.prefix}{self._component.operation()}"

class SuffixDecorator(Decorator):
    def __init__(self, component: Component, suffix: str):
        super().__init__(component)
        self.suffix = suffix
    
    def operation(self) -> str:
        return f"{self._component.operation()}{self.suffix}"

class DecoratorBuilder:
    def __init__(self, component: Component):
        self._component = component
    
    def add_border(self, char: str = "*") -> 'DecoratorBuilder':
        self._component = BorderDecorator(self._component, char)
        return self
    
    def add_color(self, color: str = 'green') -> 'DecoratorBuilder':
        self._component = ColorDecorator(self._component, color)
        return self
    
    def add_uppercase(self) -> 'DecoratorBuilder':
        self._component = UpperCaseDecorator(self._component)
        return self
    
    def add_prefix(self, prefix: str) -> 'DecoratorBuilder':
        self._component = PrefixDecorator(self._component, prefix)
        return self
    
    def add_suffix(self, suffix: str) -> 'DecoratorBuilder':
        self._component = SuffixDecorator(self._component, suffix)
        return self
    
    def build(self) -> Component:
        return self._component

class FunctionDecorator:
    def __init__(self, func: Callable):
        self.func = func
        self._decorators: List[Callable] = []
    
    def add_decorator(self, decorator: Callable) -> 'FunctionDecorator':
        self._decorators.append(decorator)
        return self
    
    def __call__(self, *args, **kwargs):
        result = self.func(*args, **kwargs)
        
        for decorator in reversed(self._decorators):
            result = decorator(result)
        
        return result

def decorator_chain(*decorators: Callable):
    def wrapper(func: Callable):
        @wraps(func)
        def wrapped(*args, **kwargs):
            result = func(*args, **kwargs)
            for decorator in reversed(decorators):
                result = decorator(result)
            return result
        return wrapped
    return wrapper

class CachedDecorator:
    def __init__(self, func: Callable):
        self.func = func
        self._cache: Dict[str, Any] = {}
    
    def __call__(self, *args, **kwargs):
        key = str(args) + str(kwargs)
        
        if key not in self._cache:
            self._cache[key] = self.func(*args, **kwargs)
        
        return self._cache[key]
    
    def clear_cache(self):
        self._cache.clear()

class ValidatedDecorator:
    def __init__(self, func: Callable, validator: Callable):
        self.func = func
        self.validator = validator
    
    def __call__(self, *args, **kwargs):
        if not self.validator(*args, **kwargs):
            raise ValueError("参数验证失败")
        return self.func(*args, **kwargs)

def main():
    print("=== 组件装饰器 ===")
    component = Component("Hello World")
    
    decorated = (DecoratorBuilder(component)
                 .add_uppercase()
                 .add_prefix("[INFO] ")
                 .add_suffix("!")
                 .build())
    
    print(f"结果: {decorated.operation()}")
    
    print("\n=== 边框装饰器 ===")
    bordered = BorderDecorator(component)
    print(bordered.operation())
    
    print("\n=== 函数装饰器链 ===")
    def add_prefix(s, prefix="["):
        return f"{prefix}{s}"
    
    def add_suffix(s, suffix="]"):
        return f"{s}{suffix}"
    
    def to_upper(s):
        return s.upper()
    
    @decorator_chain(to_upper, lambda s: add_prefix(s, ">>"), lambda s: add_suffix(s, "<<"))
    def get_message():
        return "hello"
    
    print(f"装饰后: {get_message()}")
    
    print("\n=== 缓存装饰器 ===")
    call_count = 0
    
    @CachedDecorator
    def expensive_computation(n):
        nonlocal call_count
        call_count += 1
        return n * n
    
    print(f"第一次调用: {expensive_computation(5)}, 调用次数: {call_count}")
    print(f"第二次调用: {expensive_computation(5)}, 调用次数: {call_count}")
    print(f"不同参数: {expensive_computation(10)}, 调用次数: {call_count}")


if __name__ == "__main__":
    main()
