# -----------------------------
# 题目：实现简单的路由系统。
# -----------------------------

import re
from typing import Dict, List, Callable, Any, Tuple
from dataclasses import dataclass
from enum import Enum

class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"

@dataclass
class Route:
    method: HttpMethod
    pattern: str
    handler: Callable
    params: Dict[str, str] = None

class Request:
    def __init__(self, method: str, path: str, headers: Dict = None, body: Any = None):
        self.method = HttpMethod(method.upper())
        self.path = path
        self.headers = headers or {}
        self.body = body
        self.params = {}
        self.query = {}

class Response:
    def __init__(self, status: int = 200, body: Any = None, headers: Dict = None):
        self.status = status
        self.body = body
        self.headers = headers or {}
    
    @classmethod
    def json(cls, data: Any, status: int = 200):
        return cls(status, data, {'Content-Type': 'application/json'})
    
    @classmethod
    def text(cls, text: str, status: int = 200):
        return cls(status, text, {'Content-Type': 'text/plain'})
    
    @classmethod
    def not_found(cls):
        return cls(404, {'error': 'Not Found'})
    
    @classmethod
    def method_not_allowed(cls):
        return cls(405, {'error': 'Method Not Allowed'})

class Router:
    def __init__(self):
        self.routes: List[Route] = []
        self.middleware: List[Callable] = []
    
    def add_route(self, method: HttpMethod, pattern: str, handler: Callable):
        self.routes.append(Route(method=method, pattern=pattern, handler=handler))
    
    def get(self, pattern: str):
        def decorator(handler: Callable):
            self.add_route(HttpMethod.GET, pattern, handler)
            return handler
        return decorator
    
    def post(self, pattern: str):
        def decorator(handler: Callable):
            self.add_route(HttpMethod.POST, pattern, handler)
            return handler
        return decorator
    
    def put(self, pattern: str):
        def decorator(handler: Callable):
            self.add_route(HttpMethod.PUT, pattern, handler)
            return handler
        return decorator
    
    def delete(self, pattern: str):
        def decorator(handler: Callable):
            self.add_route(HttpMethod.DELETE, pattern, handler)
            return handler
        return decorator
    
    def use(self, middleware: Callable):
        self.middleware.append(middleware)
    
    def match(self, request: Request) -> Tuple[Route, Dict[str, str]]:
        for route in self.routes:
            if route.method != request.method:
                continue
            
            params = self._match_pattern(route.pattern, request.path)
            if params is not None:
                return route, params
        
        return None, {}
    
    def _match_pattern(self, pattern: str, path: str) -> Dict[str, str]:
        pattern_parts = pattern.strip('/').split('/')
        path_parts = path.strip('/').split('/')
        
        if len(pattern_parts) != len(path_parts):
            return None
        
        params = {}
        for pattern_part, path_part in zip(pattern_parts, path_parts):
            if pattern_part.startswith('{') and pattern_part.endswith('}'):
                param_name = pattern_part[1:-1]
                params[param_name] = path_part
            elif pattern_part.startswith(':'):
                param_name = pattern_part[1:]
                params[param_name] = path_part
            elif pattern_part != path_part:
                return None
        
        return params
    
    def handle(self, request: Request) -> Response:
        for middleware in self.middleware:
            result = middleware(request)
            if result:
                return result
        
        route, params = self.match(request)
        
        if route is None:
            return Response.not_found()
        
        request.params = params
        return route.handler(request)

class Application:
    def __init__(self):
        self.router = Router()
    
    def route(self, method: str, pattern: str):
        def decorator(handler: Callable):
            self.router.add_route(HttpMethod(method.upper()), pattern, handler)
            return handler
        return decorator
    
    def get(self, pattern: str):
        return self.router.get(pattern)
    
    def post(self, pattern: str):
        return self.router.post(pattern)
    
    def use(self, middleware: Callable):
        self.router.use(middleware)
    
    def handle_request(self, method: str, path: str, **kwargs) -> Response:
        request = Request(method, path, **kwargs)
        return self.router.handle(request)

def main():
    app = Application()
    
    @app.get('/')
    def index(request: Request) -> Response:
        return Response.json({'message': 'Hello World'})
    
    @app.get('/users')
    def list_users(request: Request) -> Response:
        return Response.json({'users': [{'id': 1, 'name': '张三'}]})
    
    @app.get('/users/{id}')
    def get_user(request: Request) -> Response:
        user_id = request.params['id']
        return Response.json({'id': user_id, 'name': f'用户{user_id}'})
    
    @app.post('/users')
    def create_user(request: Request) -> Response:
        return Response.json({'created': True, 'data': request.body}, status=201)
    
    @app.put('/users/{id}')
    def update_user(request: Request) -> Response:
        return Response.json({'updated': True, 'id': request.params['id']})
    
    @app.delete('/users/{id}')
    def delete_user(request: Request) -> Response:
        return Response.json({'deleted': True, 'id': request.params['id']})
    
    print("=== 路由测试 ===")
    
    response = app.handle_request('GET', '/')
    print(f"GET /: {response.body}")
    
    response = app.handle_request('GET', '/users')
    print(f"GET /users: {response.body}")
    
    response = app.handle_request('GET', '/users/123')
    print(f"GET /users/123: {response.body}")
    
    response = app.handle_request('POST', '/users', body={'name': '李四'})
    print(f"POST /users: {response.body}")
    
    response = app.handle_request('GET', '/not-found')
    print(f"GET /not-found: {response.body}")


if __name__ == "__main__":
    main()
