# -----------------------------
# 题目：HTTP请求模拟器。
# 描述：模拟HTTP请求和响应。
# -----------------------------

class HTTPRequest:
    def __init__(self, method, path, headers=None, body=None):
        self.method = method
        self.path = path
        self.headers = headers or {}
        self.body = body

class HTTPResponse:
    def __init__(self, status_code, status_message, headers=None, body=None):
        self.status_code = status_code
        self.status_message = status_message
        self.headers = headers or {}
        self.body = body
    
    def __str__(self):
        return f"HTTP {self.status_code} {self.status_message}"

class Router:
    def __init__(self):
        self.routes = {}
    
    def register(self, path, handler):
        self.routes[path] = handler
    
    def handle(self, request):
        if request.path in self.routes:
            return self.routes[request.path](request)
        return HTTPResponse(404, "Not Found")

def home_handler(request):
    return HTTPResponse(200, "OK", body="Welcome to Home")

def about_handler(request):
    return HTTPResponse(200, "OK", body="About Us")

def main():
    router = Router()
    router.register("/", home_handler)
    router.register("/about", about_handler)
    response = router.handle(HTTPRequest("GET", "/"))
    print(response)
    print(response.body)


if __name__ == "__main__":
    main()
