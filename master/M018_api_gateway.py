# -----------------------------
# 题目：实现API网关。
# 描述：请求路由、限流、认证、日志。
# -----------------------------

import time
import hashlib
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from functools import wraps
from collections import defaultdict
from threading import Lock

@dataclass
class Request:
    method: str
    path: str
    headers: Dict[str, str] = field(default_factory=dict)
    body: Any = None
    client_ip: str = "127.0.0.1"
    api_key: str = None

@dataclass
class Response:
    status_code: int
    body: Any
    headers: Dict[str, str] = field(default_factory=dict)

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self._lock = Lock()
    
    def is_allowed(self, client_id: str) -> bool:
        with self._lock:
            now = time.time()
            minute_ago = now - 60
            
            self.requests[client_id] = [
                t for t in self.requests[client_id] if t > minute_ago
            ]
            
            if len(self.requests[client_id]) >= self.requests_per_minute:
                return False
            
            self.requests[client_id].append(now)
            return True
    
    def get_remaining(self, client_id: str) -> int:
        with self._lock:
            now = time.time()
            minute_ago = now - 60
            count = len([t for t in self.requests[client_id] if t > minute_ago])
            return max(0, self.requests_per_minute - count)

class Authenticator:
    def __init__(self):
        self.api_keys: Dict[str, Dict[str, Any]] = {}
        self.jwt_secrets: Dict[str, str] = {}
    
    def add_api_key(self, api_key: str, user_id: str, permissions: List[str] = None):
        self.api_keys[api_key] = {
            'user_id': user_id,
            'permissions': permissions or [],
            'created_at': time.time()
        }
    
    def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        return self.api_keys.get(api_key)
    
    def generate_token(self, user_id: str, secret: str) -> str:
        data = f"{user_id}:{time.time()}:{secret}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]
    
    def validate_token(self, token: str, secret: str) -> bool:
        return len(token) == 32

class Router:
    def __init__(self):
        self.routes: Dict[str, Dict[str, Callable]] = {}
    
    def add_route(self, method: str, path: str, handler: Callable):
        if path not in self.routes:
            self.routes[path] = {}
        self.routes[path][method.upper()] = handler
    
    def match(self, method: str, path: str) -> Optional[Callable]:
        if path in self.routes:
            return self.routes[path].get(method.upper())
        
        for route_path, handlers in self.routes.items():
            if self._match_pattern(route_path, path):
                return handlers.get(method.upper())
        
        return None
    
    def _match_pattern(self, pattern: str, path: str) -> bool:
        pattern_parts = pattern.split('/')
        path_parts = path.split('/')
        
        if len(pattern_parts) != len(path_parts):
            return False
        
        for p, r in zip(pattern_parts, path_parts):
            if p.startswith('{') and p.endswith('}'):
                continue
            if p != r:
                return False
        
        return True

class Logger:
    def __init__(self):
        self.logs: List[Dict[str, Any]] = []
        self._lock = Lock()
    
    def log_request(self, request: Request, response: Response, duration: float):
        with self._lock:
            self.logs.append({
                'timestamp': time.time(),
                'method': request.method,
                'path': request.path,
                'client_ip': request.client_ip,
                'status_code': response.status_code,
                'duration_ms': duration * 1000
            })
    
    def get_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self.logs[-limit:]

class APIGateway:
    def __init__(self):
        self.router = Router()
        self.rate_limiter = RateLimiter(requests_per_minute=100)
        self.authenticator = Authenticator()
        self.logger = Logger()
        self.middlewares: List[Callable] = []
    
    def add_middleware(self, middleware: Callable):
        self.middlewares.append(middleware)
    
    def route(self, method: str, path: str):
        def decorator(handler: Callable):
            self.router.add_route(method, path, handler)
            return handler
        return decorator
    
    def handle(self, request: Request) -> Response:
        start_time = time.time()
        
        client_id = request.api_key or request.client_ip
        
        if not self.rate_limiter.is_allowed(client_id):
            return Response(429, {'error': '请求过于频繁'})
        
        if request.api_key:
            user_info = self.authenticator.validate_api_key(request.api_key)
            if not user_info:
                return Response(401, {'error': '无效的API密钥'})
            request.headers['user_id'] = user_info['user_id']
        
        handler = self.router.match(request.method, request.path)
        if not handler:
            return Response(404, {'error': '未找到路由'})
        
        try:
            response = handler(request)
            if not isinstance(response, Response):
                response = Response(200, response)
        except Exception as e:
            response = Response(500, {'error': str(e)})
        
        duration = time.time() - start_time
        self.logger.log_request(request, response, duration)
        
        response.headers['X-RateLimit-Remaining'] = str(
            self.rate_limiter.get_remaining(client_id)
        )
        
        return response

def main():
    gateway = APIGateway()
    
    gateway.authenticator.add_api_key(
        'test-api-key-123',
        'user-001',
        ['read', 'write']
    )
    
    @gateway.route('GET', '/api/users')
    def get_users(request: Request) -> Response:
        return Response(200, {'users': [{'id': 1, 'name': '张三'}]})
    
    @gateway.route('POST', '/api/users')
    def create_user(request: Request) -> Response:
        return Response(201, {'id': 2, 'name': request.body.get('name', '未知')})
    
    @gateway.route('GET', '/api/health')
    def health_check(request: Request) -> Response:
        return Response(200, {'status': 'healthy'})
    
    req1 = Request('GET', '/api/users', api_key='test-api-key-123')
    resp1 = gateway.handle(req1)
    print(f"响应1: {resp1.status_code}, {resp1.body}")
    
    req2 = Request('GET', '/api/health')
    resp2 = gateway.handle(req2)
    print(f"响应2: {resp2.status_code}, {resp2.body}")
    
    req3 = Request('GET', '/api/unknown')
    resp3 = gateway.handle(req3)
    print(f"响应3: {resp3.status_code}, {resp3.body}")
    
    print(f"\n日志记录数: {len(gateway.logger.get_logs())}")

if __name__ == "__main__":
    main()
