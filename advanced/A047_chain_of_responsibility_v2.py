# -----------------------------
# 题目：实现简单的责任链模式。
# -----------------------------

from typing import Any, Optional
from abc import ABC, abstractmethod

class Handler(ABC):
    def __init__(self):
        self._next: Optional['Handler'] = None
    
    def set_next(self, handler: 'Handler') -> 'Handler':
        self._next = handler
        return handler
    
    def handle(self, request: Any) -> Optional[Any]:
        result = self.process(request)
        
        if result is None and self._next:
            return self._next.handle(request)
        
        return result
    
    @abstractmethod
    def process(self, request: Any) -> Optional[Any]:
        pass

class AuthenticationHandler(Handler):
    def __init__(self, valid_tokens: set):
        super().__init__()
        self.valid_tokens = valid_tokens
    
    def process(self, request: dict) -> Optional[Any]:
        token = request.get('token')
        
        if not token:
            return {'error': '缺少认证令牌', 'code': 401}
        
        if token not in self.valid_tokens:
            return {'error': '无效的令牌', 'code': 403}
        
        request['authenticated'] = True
        return None

class AuthorizationHandler(Handler):
    def __init__(self, permissions: dict):
        super().__init__()
        self.permissions = permissions
    
    def process(self, request: dict) -> Optional[Any]:
        if not request.get('authenticated'):
            return {'error': '未认证', 'code': 401}
        
        token = request.get('token')
        required_role = request.get('required_role')
        
        user_role = self.permissions.get(token)
        
        if required_role and user_role != required_role:
            return {'error': '权限不足', 'code': 403}
        
        return None

class RateLimitHandler(Handler):
    def __init__(self, max_requests: int = 10):
        super().__init__()
        self.max_requests = max_requests
        self.request_counts = {}
    
    def process(self, request: dict) -> Optional[Any]:
        client_id = request.get('client_id', 'anonymous')
        
        count = self.request_counts.get(client_id, 0)
        
        if count >= self.max_requests:
            return {'error': '请求过于频繁', 'code': 429}
        
        self.request_counts[client_id] = count + 1
        return None

class ValidationHandler(Handler):
    def __init__(self, required_fields: list):
        super().__init__()
        self.required_fields = required_fields
    
    def process(self, request: dict) -> Optional[Any]:
        missing = []
        
        for field in self.required_fields:
            if field not in request.get('data', {}):
                missing.append(field)
        
        if missing:
            return {'error': f'缺少必填字段: {missing}', 'code': 400}
        
        return None

class LoggingHandler(Handler):
    def process(self, request: dict) -> Optional[Any]:
        print(f"[LOG] 请求: {request.get('path', 'unknown')}")
        return None

class FinalHandler(Handler):
    def process(self, request: dict) -> Optional[Any]:
        return {'success': True, 'data': request.get('data', {})}

class HandlerChain:
    def __init__(self):
        self.first: Optional[Handler] = None
        self.last: Optional[Handler] = None
    
    def add(self, handler: Handler) -> 'HandlerChain':
        if self.first is None:
            self.first = handler
            self.last = handler
        else:
            self.last.set_next(handler)
            self.last = handler
        return self
    
    def execute(self, request: Any) -> Optional[Any]:
        if self.first:
            return self.first.handle(request)
        return None

def main():
    valid_tokens = {'token123', 'token456'}
    permissions = {
        'token123': 'admin',
        'token456': 'user'
    }
    
    chain = HandlerChain()
    chain.add(LoggingHandler())
    chain.add(AuthenticationHandler(valid_tokens))
    chain.add(AuthorizationHandler(permissions))
    chain.add(RateLimitHandler(max_requests=5))
    chain.add(ValidationHandler(['name', 'email']))
    chain.add(FinalHandler())
    
    print("=== 有效请求 ===")
    request = {
        'token': 'token123',
        'client_id': 'client1',
        'required_role': 'admin',
        'path': '/api/users',
        'data': {'name': '张三', 'email': 'zhang@example.com'}
    }
    result = chain.execute(request)
    print(f"结果: {result}")
    
    print("\n=== 无效令牌 ===")
    request = {
        'token': 'invalid',
        'client_id': 'client1',
        'path': '/api/users',
        'data': {'name': '张三'}
    }
    result = chain.execute(request)
    print(f"结果: {result}")
    
    print("\n=== 权限不足 ===")
    request = {
        'token': 'token456',
        'client_id': 'client1',
        'required_role': 'admin',
        'path': '/api/admin',
        'data': {'name': '张三', 'email': 'zhang@example.com'}
    }
    result = chain.execute(request)
    print(f"结果: {result}")
    
    print("\n=== 缺少字段 ===")
    request = {
        'token': 'token123',
        'client_id': 'client1',
        'path': '/api/users',
        'data': {'name': '张三'}
    }
    result = chain.execute(request)
    print(f"结果: {result}")


if __name__ == "__main__":
    main()
