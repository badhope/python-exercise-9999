# -----------------------------
# 题目：实现简单的API网关。
# 描述：支持路由、限流、认证。
# -----------------------------

import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_requests=100, window=60):
        self.max_requests = max_requests
        self.window = window
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_id):
        now = time.time()
        requests = self.requests[client_id]
        requests[:] = [t for t in requests if now - t < self.window]
        
        if len(requests) < self.max_requests:
            requests.append(now)
            return True
        return False

class Authenticator:
    def __init__(self):
        self.tokens = {}
    
    def generate_token(self, user_id):
        import uuid
        token = str(uuid.uuid4())
        self.tokens[token] = {'user_id': user_id, 'created_at': time.time()}
        return token
    
    def validate_token(self, token):
        return token in self.tokens
    
    def get_user(self, token):
        return self.tokens.get(token)

class APIGateway:
    def __init__(self):
        self.routes = {}
        self.rate_limiter = RateLimiter()
        self.authenticator = Authenticator()
        self.middleware = []
    
    def route(self, path, methods=None):
        def decorator(handler):
            self.routes[path] = {
                'handler': handler,
                'methods': methods or ['GET']
            }
            return handler
        return decorator
    
    def add_middleware(self, middleware):
        self.middleware.append(middleware)
    
    def handle(self, request):
        for mw in self.middleware:
            result = mw(request)
            if result:
                return result
        
        client_id = request.get('client_id', 'anonymous')
        if not self.rate_limiter.is_allowed(client_id):
            return {'status': 429, 'body': 'Too Many Requests'}
        
        path = request.get('path')
        if path in self.routes:
            route = self.routes[path]
            if request.get('method') in route['methods']:
                return route['handler'](request)
        
        return {'status': 404, 'body': 'Not Found'}

def main():
    gateway = APIGateway()
    
    @gateway.route('/users')
    def get_users(request):
        return {'status': 200, 'body': [{'id': 1, 'name': '张三'}]}
    
    @gateway.route('/orders')
    def get_orders(request):
        return {'status': 200, 'body': [{'id': 1, 'item': '笔记本'}]}
    
    def auth_middleware(request):
        token = request.get('token')
        if not token or not gateway.authenticator.validate_token(token):
            return {'status': 401, 'body': 'Unauthorized'}
        return None
    
    gateway.add_middleware(auth_middleware)
    
    token = gateway.authenticator.generate_token('user123')
    request = {'path': '/users', 'method': 'GET', 'client_id': 'client1', 'token': token}
    response = gateway.handle(request)
    print(f"响应: {response}")


if __name__ == "__main__":
    main()
