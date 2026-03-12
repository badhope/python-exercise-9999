# -----------------------------
# 题目：责任链模式实现请求处理中间件。
# -----------------------------

class Request:
    def __init__(self, path, method, headers=None, body=None):
        self.path = path
        self.method = method
        self.headers = headers or {}
        self.body = body or {}
        self.user = None
        self.errors = []

class Response:
    def __init__(self, status=200, body=None):
        self.status = status
        self.body = body or {}
    
    def is_success(self):
        return 200 <= self.status < 300

class Middleware:
    def __init__(self):
        self.next_middleware = None
    
    def set_next(self, middleware):
        self.next_middleware = middleware
        return middleware
    
    def handle(self, request):
        if self.next_middleware:
            return self.next_middleware.handle(request)
        return Response(200, {'message': 'OK'})

class AuthMiddleware(Middleware):
    def __init__(self, valid_tokens):
        super().__init__()
        self.valid_tokens = valid_tokens
    
    def handle(self, request):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return Response(401, {'error': 'Missing authorization token'})
        
        if token not in self.valid_tokens:
            return Response(403, {'error': 'Invalid token'})
        
        request.user = self.valid_tokens[token]
        return super().handle(request)

class RateLimitMiddleware(Middleware):
    def __init__(self, max_requests=100, window_seconds=60):
        super().__init__()
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    def handle(self, request):
        user_id = request.user.get('id') if request.user else 'anonymous'
        
        if user_id not in self.requests:
            self.requests[user_id] = []
        
        import time
        now = time.time()
        self.requests[user_id] = [t for t in self.requests[user_id] if now - t < self.window_seconds]
        
        if len(self.requests[user_id]) >= self.max_requests:
            return Response(429, {'error': 'Too many requests'})
        
        self.requests[user_id].append(now)
        return super().handle(request)

class LoggingMiddleware(Middleware):
    def handle(self, request):
        import time
        start_time = time.time()
        
        response = super().handle(request)
        
        duration = time.time() - start_time
        print(f"[LOG] {request.method} {request.path} - {response.status} ({duration:.3f}s)")
        
        return response

class ValidationMiddleware(Middleware):
    def __init__(self, required_fields):
        super().__init__()
        self.required_fields = required_fields
    
    def handle(self, request):
        if request.method in ['POST', 'PUT']:
            for field in self.required_fields:
                if field not in request.body:
                    return Response(400, {'error': f'Missing required field: {field}'})
        
        return super().handle(request)

class CORSMiddleware(Middleware):
    def __init__(self, allowed_origins):
        super().__init__()
        self.allowed_origins = allowed_origins
    
    def handle(self, request):
        origin = request.headers.get('Origin', '')
        
        if origin and origin not in self.allowed_origins:
            return Response(403, {'error': 'Origin not allowed'})
        
        response = super().handle(request)
        response.headers = {'Access-Control-Allow-Origin': origin or '*'}
        return response

class Application:
    def __init__(self):
        self.middleware_chain = None
    
    def use(self, middleware):
        if not self.middleware_chain:
            self.middleware_chain = middleware
        else:
            current = self.middleware_chain
            while current.next_middleware:
                current = current.next_middleware
            current.set_next(middleware)
    
    def handle(self, request):
        if self.middleware_chain:
            return self.middleware_chain.handle(request)
        return Response(200, {'message': 'OK'})

def main():
    app = Application()
    
    valid_tokens = {
        'token123': {'id': 1, 'name': '张三'},
        'token456': {'id': 2, 'name': '李四'}
    }
    
    app.use(LoggingMiddleware())
    app.use(CORSMiddleware(['http://localhost:3000']))
    app.use(AuthMiddleware(valid_tokens))
    app.use(RateLimitMiddleware(max_requests=5))
    app.use(ValidationMiddleware(['name', 'email']))
    
    print("=== 测试1: 无Token ===")
    req1 = Request('/api/users', 'GET', {})
    print(f"响应: {app.handle(req1).body}")
    
    print("\n=== 测试2: 有效Token ===")
    req2 = Request('/api/users', 'GET', {'Authorization': 'Bearer token123'})
    print(f"响应: {app.handle(req2).body}")
    
    print("\n=== 测试3: POST缺少字段 ===")
    req3 = Request('/api/users', 'POST', {'Authorization': 'Bearer token123'}, {'name': '王五'})
    print(f"响应: {app.handle(req3).body}")
    
    print("\n=== 测试4: POST完整字段 ===")
    req4 = Request('/api/users', 'POST', {'Authorization': 'Bearer token123'}, {'name': '王五', 'email': 'wang@example.com'})
    print(f"响应: {app.handle(req4).body}")


if __name__ == "__main__":
    main()
