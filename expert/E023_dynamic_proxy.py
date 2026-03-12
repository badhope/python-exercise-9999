# -----------------------------
# 题目：实现动态代理。
# -----------------------------

import functools
from typing import Any, Callable, Dict, List

class MethodInterceptor:
    def before(self, method_name: str, args: tuple, kwargs: dict):
        pass
    
    def after(self, method_name: str, result: Any):
        pass
    
    def on_exception(self, method_name: str, exception: Exception):
        pass

class LoggingInterceptor(MethodInterceptor):
    def before(self, method_name: str, args: tuple, kwargs: dict):
        print(f"[调用] {method_name}({args}, {kwargs})")
    
    def after(self, method_name: str, result: Any):
        print(f"[返回] {method_name} -> {result}")
    
    def on_exception(self, method_name: str, exception: Exception):
        print(f"[异常] {method_name}: {exception}")

class TimingInterceptor(MethodInterceptor):
    import time
    
    def before(self, method_name: str, args: tuple, kwargs: dict):
        self._start = self.time.time()
    
    def after(self, method_name: str, result: Any):
        duration = self.time.time() - self._start
        print(f"[耗时] {method_name}: {duration:.4f}秒")

class Proxy:
    def __init__(self, target: Any):
        self._target = target
        self._interceptors: List[MethodInterceptor] = []
    
    def add_interceptor(self, interceptor: MethodInterceptor):
        self._interceptors.append(interceptor)
    
    def __getattr__(self, name: str):
        attr = getattr(self._target, name)
        
        if callable(attr):
            @functools.wraps(attr)
            def wrapped(*args, **kwargs):
                for interceptor in self._interceptors:
                    interceptor.before(name, args, kwargs)
                
                try:
                    result = attr(*args, **kwargs)
                    for interceptor in self._interceptors:
                        interceptor.after(name, result)
                    return result
                except Exception as e:
                    for interceptor in self._interceptors:
                        interceptor.on_exception(name, e)
                    raise
            
            return wrapped
        
        return attr

class ProxyFactory:
    @staticmethod
    def create(target: Any, *interceptors: MethodInterceptor) -> Proxy:
        proxy = Proxy(target)
        for interceptor in interceptors:
            proxy.add_interceptor(interceptor)
        return proxy

class UserService:
    def __init__(self):
        self.users: Dict[int, dict] = {}
        self.next_id = 1
    
    def create_user(self, name: str, email: str) -> dict:
        user_id = self.next_id
        self.next_id += 1
        user = {'id': user_id, 'name': name, 'email': email}
        self.users[user_id] = user
        return user
    
    def get_user(self, user_id: int) -> dict:
        return self.users.get(user_id)
    
    def delete_user(self, user_id: int) -> bool:
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False

class CachingInterceptor(MethodInterceptor):
    def __init__(self):
        self._cache: Dict[str, Any] = {}
    
    def before(self, method_name: str, args: tuple, kwargs: dict):
        if method_name.startswith('get_'):
            cache_key = f"{method_name}:{args}:{kwargs}"
            if cache_key in self._cache:
                return self._cache[cache_key]
        return None
    
    def after(self, method_name: str, result: Any):
        if method_name.startswith('get_'):
            pass

class AccessControlInterceptor(MethodInterceptor):
    def __init__(self, allowed_methods: List[str]):
        self.allowed_methods = allowed_methods
    
    def before(self, method_name: str, args: tuple, kwargs: dict):
        if method_name not in self.allowed_methods:
            raise PermissionError(f"方法 {method_name} 不允许访问")

def main():
    print("=== 基本代理 ===")
    service = UserService()
    proxy = ProxyFactory.create(service, LoggingInterceptor())
    
    proxy.create_user("张三", "zhang@example.com")
    proxy.get_user(1)
    
    print("\n=== 多个拦截器 ===")
    proxy2 = ProxyFactory.create(
        UserService(),
        LoggingInterceptor(),
        TimingInterceptor()
    )
    
    proxy2.create_user("李四", "li@example.com")
    
    print("\n=== 访问控制 ===")
    proxy3 = ProxyFactory.create(
        UserService(),
        AccessControlInterceptor(['create_user', 'get_user'])
    )
    
    proxy3.create_user("王五", "wang@example.com")
    
    try:
        proxy3.delete_user(1)
    except PermissionError as e:
        print(f"权限错误: {e}")


if __name__ == "__main__":
    main()
