# -----------------------------
# 题目：实现简易AOP框架。
# -----------------------------

class Aspect:
    def before(self, method, *args, **kwargs):
        pass
    
    def after(self, method, result, *args, **kwargs):
        pass

class LoggingAspect(Aspect):
    def before(self, method, *args, **kwargs):
        print(f"[日志] 调用方法: {method.__name__}")
    
    def after(self, method, result, *args, **kwargs):
        print(f"[日志] 方法 {method.__name__} 返回: {result}")

class TimingAspect(Aspect):
    def before(self, method, *args, **kwargs):
        import time
        self._start = time.time()
    
    def after(self, method, result, *args, **kwargs):
        import time
        print(f"[性能] {method.__name__} 耗时: {time.time() - self._start:.4f}s")

def aop(*aspects):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for aspect in aspects:
                aspect.before(func, *args, **kwargs)
            result = func(*args, **kwargs)
            for aspect in reversed(aspects):
                aspect.after(func, result, *args, **kwargs)
            return result
        return wrapper
    return decorator

@aop(LoggingAspect(), TimingAspect())
def add(a, b):
    return a + b

def main():
    print(add(3, 5))


if __name__ == "__main__":
    main()
