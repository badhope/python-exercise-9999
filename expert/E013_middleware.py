# -----------------------------
# 题目：实现简单的中间件系统。
# 描述：支持请求/响应处理链。
# -----------------------------

class Request:
    def __init__(self, path, method='GET', headers=None, body=None):
        self.path = path
        self.method = method
        self.headers = headers or {}
        self.body = body
        self.state = {}

class Response:
    def __init__(self, status=200, body=''):
        self.status = status
        self.body = body
        self.headers = {}

class Middleware:
    def process_request(self, request):
        return request
    
    def process_response(self, request, response):
        return response

class LoggingMiddleware(Middleware):
    def process_request(self, request):
        print(f"[请求] {request.method} {request.path}")
        return request
    
    def process_response(self, request, response):
        print(f"[响应] {response.status}")
        return response

class AuthMiddleware(Middleware):
    def process_request(self, request):
        token = request.headers.get('Authorization')
        if not token:
            return None
        request.state['user'] = 'authenticated_user'
        return request

class Application:
    def __init__(self):
        self.middlewares = []
        self.routes = {}
    
    def add_middleware(self, middleware):
        self.middlewares.append(middleware)
    
    def route(self, path):
        def decorator(handler):
            self.routes[path] = handler
            return handler
        return decorator
    
    def handle(self, request):
        for middleware in self.middlewares:
            request = middleware.process_request(request)
            if request is None:
                return Response(401, "Unauthorized")
        
        handler = self.routes.get(request.path)
        if handler:
            response = handler(request)
        else:
            response = Response(404, "Not Found")
        
        for middleware in reversed(self.middlewares):
            response = middleware.process_response(request, response)
        
        return response

def main():
    app = Application()
    app.add_middleware(LoggingMiddleware())
    app.add_middleware(AuthMiddleware())
    
    @app.route('/')
    def index(request):
        return Response(200, "Hello World")
    
    request = Request('/', 'GET', {'Authorization': 'token123'})
    response = app.handle(request)
    print(f"响应: {response.body}")


if __name__ == "__main__":
    main()
