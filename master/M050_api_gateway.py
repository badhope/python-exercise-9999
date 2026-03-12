# -----------------------------
# 题目：实现API网关。
# -----------------------------

import re
import urllib.request
import urllib.parse

class Route:
    def __init__(self, path, method, handler):
        self.path = path
        self.method = method
        self.handler = handler
        self.path_pattern = re.compile(path.replace("{param}", r"(?P<param>[^/]+)"))

class APIGateway:
    def __init__(self):
        self.routes = []
        self.middleware = []
    
    def add_route(self, path, method, handler):
        route = Route(path, method, handler)
        self.routes.append(route)
        return self
    
    def use(self, middleware):
        self.middleware.append(middleware)
        return self
    
    def handle_request(self, path, method):
        for middleware in self.middleware:
            path, method = middleware(path, method)
            if path is None:
                return {"error": "Forbidden"}, 403
        
        for route in self.routes:
            match = route.path_pattern.match(path)
            if match and route.method == method:
                params = match.groupdict()
                return route.handler(params)
        
        return {"error": "Not Found"}, 404

def auth_middleware(path, method):
    if path.startswith("/admin") and method == "POST":
        return None, None
    return path, method

def get_users(params):
    return {"users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}

def get_user(params):
    return {"user": {"id": params.get("id"), "name": "User"}}

def create_user(params):
    return {"message": "User created", "id": 3}, 201

if __name__ == "__main__":
    gateway = APIGateway()
    
    gateway.use(auth_middleware)
    gateway.add_route("/users", "GET", get_users)
    gateway.add_route("/users/{id}", "GET", get_user)
    gateway.add_route("/users", "POST", create_user)
    
    response = gateway.handle_request("/users", "GET")
    print(f"GET /users: {response}")
    
    response = gateway.handle_request("/users/123", "GET")
    print(f"GET /users/123: {response}")
    
    response = gateway.handle_request("/admin/config", "POST")
    print(f"POST /admin/config: {response}")
