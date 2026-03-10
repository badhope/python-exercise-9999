# -----------------------------
# 题目：实现Web服务器。
# -----------------------------

import socket
from urllib.parse import parse_qs

class Request:
    def __init__(self, data):
        lines = data.split('\r\n')
        if lines:
            parts = lines[0].split()
            if len(parts) >= 2:
                self.method = parts[0]
                self.path = parts[1].split('?')[0]
                self.query = {}
                if '?' in parts[1]:
                    query_string = parts[1].split('?')[1]
                    self.query = parse_qs(query_string)

class Response:
    def __init__(self, status=200, body=""):
        self.status = status
        self.body = body
    
    def to_bytes(self):
        status_messages = {200: "OK", 404: "Not Found", 500: "Internal Server Error"}
        header = f"HTTP/1.1 {self.status} {status_messages.get(self.status, 'OK')}\r\n"
        header += f"Content-Length: {len(self.body)}\r\n"
        header += "Content-Type: text/html\r\n\r\n"
        return header.encode() + self.body.encode()

class WebServer:
    def __init__(self, host='0.0.0.0', port=8080):
        self.host = host
        self.port = port
        self.routes = {}
    
    def route(self, path):
        def decorator(func):
            self.routes[path] = func
            return func
        return decorator
    
    def handle_request(self, client_sock):
        try:
            data = client_sock.recv(4096).decode()
            if data:
                request = Request(data)
                handler = self.routes.get(request.path)
                if handler:
                    response = handler(request)
                else:
                    response = Response(404, "<h1>404 Not Found</h1>")
                client_sock.sendall(response.to_bytes())
        finally:
            client_sock.close()
    
    def start(self):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((self.host, self.port))
        server_sock.listen(5)
        print(f"服务器运行在 http://{self.host}:{self.port}")
        while True:
            client_sock, addr = server_sock.accept()
            self.handle_request(client_sock)

def main():
    server = WebServer()
    
    @server.route("/")
    def index(req):
        return Response(body="<h1>Hello World</h1>")
    
    @server.route("/hello")
    def hello(req):
        return Response(body="<h1>Hello!</h1>")
    
    print("启动服务器...")


if __name__ == "__main__":
    main()
