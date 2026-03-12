# -----------------------------
# 题目：实现AOP框架。
# 描述：支持切面定义、通知类型、切入点表达式。
# -----------------------------

import time
import functools
from abc import ABC, abstractmethod
from typing import Callable, Any, List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

class AdviceType(Enum):
    BEFORE = "before"
    AFTER = "after"
    AROUND = "around"
    AFTER_RETURNING = "after_returning"
    AFTER_THROWING = "after_throwing"

@dataclass
class JoinPoint:
    target: Any
    method_name: str
    args: tuple
    kwargs: dict
    result: Any = None
    exception: Exception = None
    proceed: Callable = None

class Aspect(ABC):
    @abstractmethod
    def get_pointcut(self) -> str:
        pass
    
    def before(self, joinpoint: JoinPoint):
        pass
    
    def after(self, joinpoint: JoinPoint):
        pass
    
    def around(self, joinpoint: JoinPoint) -> Any:
        return joinpoint.proceed(*joinpoint.args, **joinpoint.kwargs)
    
    def after_returning(self, joinpoint: JoinPoint, result: Any):
        pass
    
    def after_throwing(self, joinpoint: JoinPoint, exception: Exception):
        pass

class LoggingAspect(Aspect):
    def get_pointcut(self) -> str:
        return "service.*"
    
    def before(self, joinpoint: JoinPoint):
        print(f"[日志] 调用 {joinpoint.method_name}, 参数: {joinpoint.args}")
    
    def after_returning(self, joinpoint: JoinPoint, result: Any):
        print(f"[日志] {joinpoint.method_name} 返回: {result}")

class TimingAspect(Aspect):
    def get_pointcut(self) -> str:
        return "*.*"
    
    def around(self, joinpoint: JoinPoint) -> Any:
        start = time.time()
        try:
            result = joinpoint.proceed(*joinpoint.args, **joinpoint.kwargs)
            elapsed = (time.time() - start) * 1000
            print(f"[耗时] {joinpoint.method_name}: {elapsed:.2f}ms")
            return result
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            print(f"[耗时] {joinpoint.method_name} 异常: {elapsed:.2f}ms")
            raise

class RetryAspect(Aspect):
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
    
    def get_pointcut(self) -> str:
        return "*.retry_*"
    
    def around(self, joinpoint: JoinPoint) -> Any:
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                return joinpoint.proceed(*joinpoint.args, **joinpoint.kwargs)
            except Exception as e:
                last_exception = e
                print(f"[重试] {joinpoint.method_name} 第{attempt + 1}次失败")
        
        raise last_exception

class AOPProxy:
    def __init__(self, target: Any, aspects: List[Aspect]):
        self._target = target
        self._aspects = aspects
        self._method_aspects: Dict[str, List[Aspect]] = {}
        
        self._build_method_aspects()
    
    def _build_method_aspects(self):
        target_name = self._target.__class__.__name__.lower()
        
        for method_name in dir(self._target):
            if method_name.startswith('_'):
                continue
            
            method_key = f"{target_name}.{method_name}"
            
            for aspect in self._aspects:
                pointcut = aspect.get_pointcut()
                
                if self._match_pointcut(pointcut, target_name, method_name):
                    if method_name not in self._method_aspects:
                        self._method_aspects[method_name] = []
                    self._method_aspects[method_name].append(aspect)
    
    def _match_pointcut(self, pointcut: str, target_name: str, method_name: str) -> bool:
        if pointcut == "*.*":
            return True
        
        target_pattern, method_pattern = pointcut.split('.')
        
        target_match = (target_pattern == '*' or 
                       target_pattern.lower() == target_name)
        
        method_match = (method_pattern == '*' or 
                       method_pattern == method_name or
                       method_pattern.startswith('*') and method_name.endswith(method_pattern[1:]) or
                       method_pattern.endswith('*') and method_name.startswith(method_pattern[:-1]))
        
        return target_match and method_match
    
    def __getattr__(self, name: str):
        attr = getattr(self._target, name)
        
        if not callable(attr):
            return attr
        
        aspects = self._method_aspects.get(name, [])
        
        if not aspects:
            return attr
        
        @functools.wraps(attr)
        def wrapper(*args, **kwargs):
            joinpoint = JoinPoint(
                target=self._target,
                method_name=name,
                args=args,
                kwargs=kwargs,
                proceed=attr
            )
            
            for aspect in aspects:
                aspect.before(joinpoint)
            
            try:
                around_aspects = [a for a in aspects if hasattr(a, 'around')]
                
                if around_aspects:
                    result = around_aspects[0].around(joinpoint)
                else:
                    result = attr(*args, **kwargs)
                
                joinpoint.result = result
                
                for aspect in aspects:
                    aspect.after_returning(joinpoint, result)
                
                return result
            
            except Exception as e:
                joinpoint.exception = e
                for aspect in aspects:
                    aspect.after_throwing(joinpoint, e)
                raise
            
            finally:
                for aspect in aspects:
                    aspect.after(joinpoint)
        
        return wrapper

class AOPContainer:
    def __init__(self):
        self._aspects: List[Aspect] = []
    
    def add_aspect(self, aspect: Aspect):
        self._aspects.append(aspect)
    
    def proxy(self, target: Any) -> AOPProxy:
        return AOPProxy(target, self._aspects)

class UserService:
    def get_user(self, user_id: int) -> dict:
        return {"id": user_id, "name": f"用户{user_id}"}
    
    def create_user(self, name: str, email: str) -> dict:
        return {"id": 1, "name": name, "email": email}
    
    def retry_operation(self, data: str) -> str:
        import random
        if random.random() < 0.5:
            raise Exception("随机失败")
        return f"处理成功: {data}"

def main():
    container = AOPContainer()
    container.add_aspect(LoggingAspect())
    container.add_aspect(TimingAspect())
    container.add_aspect(RetryAspect(max_retries=3))
    
    service = UserService()
    proxied_service = container.proxy(service)
    
    user = proxied_service.get_user(1)
    print(f"结果: {user}\n")
    
    new_user = proxied_service.create_user("张三", "zhang@example.com")
    print(f"结果: {new_user}\n")

if __name__ == "__main__":
    main()
