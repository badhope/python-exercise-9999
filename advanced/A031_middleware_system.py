# -----------------------------
# 题目：实现简单的中间件系统。
# -----------------------------

from typing import Callable, Dict, Any, List
from dataclasses import dataclass

@dataclass
class Request:
    method: str
    path: str
    headers: Dict[str, str]
    body: Any = None
    params: Dict[str, str] = None
    user: Dict[str, Any] = None

@dataclass
class Response:
    status: int
    body: Any
    headers: Dict[str, str] = None

class Middleware:
    def __init__(self):
        self.next_middleware: Callable = None
    
    def set_next(self, middleware: 'Middleware'):
        self.next_middleware = middleware
        return middleware
    
    def handle(self, request: Request) -> Response:
        if self.next_middleware:
            return self.next_middleware.handle(request)
        return Response(200, {'message': 'OK'})

class AuthMiddleware(Middleware):
    def __init__(self, token_validator: Callable):
        super().__init__()
        self.token_validator = token_validator
    
    def handle(self, request: Request) -> Response:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return Response(401, {'error': '未提供认证令牌'})
        
        user = self.token_validator(token)
        if not user:
            return Response(403, {'error': '无效的令牌'})
        
        request.user = user
        return super().handle(request)

class LoggingMiddleware(Middleware):
    def handle(self, request: Request) -> Response:
        import time
        start = time.time()
        
        response = super().handle(request)
        
        duration = time.time() - start
        print(f"[LOG] {request.method} {request.path} - {response.status} ({duration:.3f}s)")
        
        return response

class CORSMiddleware(Middleware):
    def __init__(self, allowed_origins: List[str]):
        super().__init__()
        self.allowed_origins = allowed_origins
    
    def handle(self, request: Request) -> Response:
        origin = request.headers.get('Origin', '')
        
        if request.method == 'OPTIONS':
            return Response(200, '', {
                'Access-Control-Allow-Origin': origin or '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            })
        
        response = super().handle(request)
        
        if origin in self.allowed_origins or '*' in self.allowed_origins:
            if response.headers is None:
                response.headers = {}
            response.headers['Access-Control-Allow-Origin'] = origin or '*'
        
        return response

class RateLimitMiddleware(Middleware):
    def __init__(self, max_requests: int = 100, window: int = 60):
        super().__init__()
        self.max_requests = max_requests
        self.window = window
        self.requests: Dict[str, List[float]] = {}
    
    def handle(self, request: Request) -> Response:
        import time
        client_id = request.headers.get('X-Client-ID', request.user.get('id', 'anonymous') if request.user else 'anonymous')
        
        now = time.time()
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        self.requests[client_id] = [t for t in self.requests[client_id] if now - t < self.window]
        
        if len(self.requests[client_id]) >= self.max_requests:
            return Response(429, {'error': '请求过于频繁'})
        
        self.requests[client_id].append(now)
        return super().handle(request)

class MiddlewarePipeline:
    def __init__(self):
        self.middlewares: List[Middleware] = []
        self.handler: Callable = None
    
    def add(self, middleware: Middleware) -> 'MiddlewarePipeline':
        self.middlewares.append(middleware)
        return self
    
    def set_handler(self, handler: Callable):
        self.handler = handler
    
    def build(self):
        if not self.middlewares:
            return
        
        for i in range(len(self.middlewares) - 1):
            self.middlewares[i].set_next(self.middlewares[i + 1])
        
        if self.handler:
            class HandlerMiddleware(Middleware):
                def __init__(self, h):
                    super().__init__()
                    self.handler = h
                
                def handle(self, request):
                    return self.handler(request)
            
            self.middlewares[-1].set_next(HandlerMiddleware(self.handler))
    
    def execute(self, request: Request) -> Response:
        if self.middlewares:
            self.build()
            return self.middlewares[0].handle(request)
        
        if self.handler:
            return self.handler(request)
        
        return Response(200, {'message': 'OK'})

def main():
    def validate_token(token: str) -> Dict:
        valid_tokens = {
            'token123': {'id': 1, 'name': '张三', 'role': 'admin'},
            'token456': {'id': 2, 'name': '李四', 'role': 'user'}
        }
        return valid_tokens.get(token)
    
    def api_handler(request: Request) -> Response:
        return Response(200, {'message': f'Hello, {request.user["name"]}!'})
    
    pipeline = MiddlewarePipeline()
    pipeline.add(LoggingMiddleware())
    pipeline.add(CORSMiddleware(['http://localhost:3000']))
    pipeline.add(AuthMiddleware(validate_token))
    pipeline.add(RateLimitMiddleware(max_requests=5))
    pipeline.set_handler(api_handler)
    
    print("=== 测试无Token请求 ===")
    request = Request('GET', '/api/users', {})
    response = pipeline.execute(request)
    print(f"响应: {response.status} - {response.body}")
    
    print("\n=== 测试有效Token请求 ===")
    request = Request('GET', '/api/users', {'Authorization': 'Bearer token123'})
    response = pipeline.execute(request)
    print(f"响应: {response.status} - {response.body}")
    
    print("\n=== 测试OPTIONS请求 ===")
    request = Request('OPTIONS', '/api/users', {'Origin': 'http://localhost:3000'})
    response = pipeline.execute(request)
    print(f"响应: {response.status} - {response.headers}")


if __name__ == "__main__":
    main()
