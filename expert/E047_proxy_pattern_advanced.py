# -----------------------------
# 题目：实现代理模式高级版。
# -----------------------------

from typing import Any, Callable, Dict, List, Optional
from functools import wraps
import time

class Subject:
    def request(self) -> str:
        return "真实请求"

class RealSubject(Subject):
    def request(self) -> str:
        return "处理真实请求"

class Proxy(Subject):
    def __init__(self, real_subject: RealSubject):
        self._real_subject = real_subject
    
    def request(self) -> str:
        return self._real_subject.request()

class VirtualProxy(Subject):
    def __init__(self):
        self._real_subject: Optional[RealSubject] = None
    
    def request(self) -> str:
        if self._real_subject is None:
            print("延迟加载真实对象")
            self._real_subject = RealSubject()
        return self._real_subject.request()

class ProtectionProxy(Subject):
    def __init__(self, real_subject: RealSubject, authorized: bool = False):
        self._real_subject = real_subject
        self._authorized = authorized
    
    def request(self) -> str:
        if not self._authorized:
            return "访问被拒绝"
        return self._real_subject.request()

class CachingProxy(Subject):
    def __init__(self, real_subject: RealSubject, ttl: int = 60):
        self._real_subject = real_subject
        self._ttl = ttl
        self._cache: Dict[str, tuple] = {}
    
    def request(self) -> str:
        key = "request"
        
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp < self._ttl:
                return f"[缓存] {value}"
        
        result = self._real_subject.request()
        self._cache[key] = (result, time.time())
        return result

class LoggingProxy(Subject):
    def __init__(self, real_subject: RealSubject):
        self._real_subject = real_subject
    
    def request(self) -> str:
        print(f"[LOG] 调用 request 方法")
        start = time.time()
        result = self._real_subject.request()
        duration = time.time() - start
        print(f"[LOG] 执行时间: {duration:.4f}秒")
        return result

class SmartProxy(Subject):
    def __init__(self, real_subject: RealSubject):
        self._real_subject = real_subject
        self._request_count = 0
    
    def request(self) -> str:
        self._request_count += 1
        return f"[第{self._request_count}次] {self._real_subject.request()}"
    
    def get_stats(self) -> dict:
        return {'request_count': self._request_count}

class ProxyFactory:
    @staticmethod
    def create_virtual() -> VirtualProxy:
        return VirtualProxy()
    
    @staticmethod
    def create_protection(authorized: bool = False) -> ProtectionProxy:
        return ProtectionProxy(RealSubject(), authorized)
    
    @staticmethod
    def create_caching(ttl: int = 60) -> CachingProxy:
        return CachingProxy(RealSubject(), ttl)
    
    @staticmethod
    def create_logging() -> LoggingProxy:
        return LoggingProxy(RealSubject())

def proxy_decorator(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[PROXY] 调用 {func.__name__}")
        result = func(*args, **kwargs)
        print(f"[PROXY] 返回 {result}")
        return result
    return wrapper

class DynamicProxy:
    def __init__(self, target: Any):
        self._target = target
        self._interceptors: List[Callable] = []
    
    def add_interceptor(self, interceptor: Callable):
        self._interceptors.append(interceptor)
        return self
    
    def __getattr__(self, name: str):
        attr = getattr(self._target, name)
        
        if callable(attr):
            @wraps(attr)
            def wrapped(*args, **kwargs):
                for interceptor in self._interceptors:
                    interceptor(name, args, kwargs)
                return attr(*args, **kwargs)
            return wrapped
        
        return attr

def main():
    print("=== 虚拟代理 ===")
    virtual = VirtualProxy()
    print(f"第一次请求: {virtual.request()}")
    print(f"第二次请求: {virtual.request()}")
    
    print("\n=== 保护代理 ===")
    unauthorized = ProtectionProxy(RealSubject(), authorized=False)
    print(f"未授权: {unauthorized.request()}")
    
    authorized = ProtectionProxy(RealSubject(), authorized=True)
    print(f"已授权: {authorized.request()}")
    
    print("\n=== 缓存代理 ===")
    caching = CachingProxy(RealSubject(), ttl=1)
    print(f"第一次: {caching.request()}")
    print(f"第二次(缓存): {caching.request()}")
    
    print("\n=== 日志代理 ===")
    logging_proxy = LoggingProxy(RealSubject())
    print(f"结果: {logging_proxy.request()}")
    
    print("\n=== 智能代理 ===")
    smart = SmartProxy(RealSubject())
    print(f"请求1: {smart.request()}")
    print(f"请求2: {smart.request()}")
    print(f"统计: {smart.get_stats()}")
    
    print("\n=== 动态代理 ===")
    class Service:
        def process(self, data: str) -> str:
            return f"处理: {data}"
    
    def log_interceptor(name, args, kwargs):
        print(f"拦截: {name}({args})")
    
    proxy = DynamicProxy(Service()).add_interceptor(log_interceptor)
    print(f"结果: {proxy.process('test')}")


if __name__ == "__main__":
    main()
