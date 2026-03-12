# -----------------------------
# 题目：实现AOP框架。
# -----------------------------

import functools
from collections import defaultdict

class Aspect:
    def before(self, *args, **kwargs):
        pass
    
    def after(self, *args, **kwargs):
        pass
    
    def on_exception(self, exception):
        raise exception

class AOP:
    def __init__(self):
        self.aspects = defaultdict(list)
    
    def register_aspect(self, method_name, aspect):
        self.aspects[method_name].append(aspect)
    
    def weave(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            aspects = self.aspects.get(func.__name__, [])
            
            for aspect in aspects:
                aspect.before(*args, **kwargs)
            
            try:
                result = func(*args, **kwargs)
                for aspect in aspects:
                    aspect.after(result)
                return result
            except Exception as e:
                for aspect in aspects:
                    aspect.on_exception(e)
                raise
        
        return wrapper
    
    def apply_to_method(self, method):
        return self.weave(method)

class LoggingAspect(Aspect):
    def before(self, *args, **kwargs):
        print(f"Calling with args={args}, kwargs={kwargs}")
    
    def after(self, result):
        print(f"Returned: {result}")

class TimingAspect(Aspect):
    import time
    
    def before(self, *args, **kwargs):
        self.start = time.time()
    
    def after(self, result):
        elapsed = time.time() - self.start
        print(f"Execution time: {elapsed:.4f}s")

if __name__ == "__main__":
    aop = AOP()
    aop.register_aspect("calculate", LoggingAspect())
    aop.register_aspect("calculate", TimingAspect())
    
    @aop.weave
    def calculate(a, b):
        return a + b
    
    result = calculate(2, 3)
    print(f"Result: {result}")
