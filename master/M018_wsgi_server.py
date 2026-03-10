# -----------------------------
# 题目：实现简单的WSGI服务器。
# -----------------------------

import socket
import sys
from io import StringIO

class WSGIEnvironment:
    def __init__(self, method, path, query_string, headers):
        self.method = method
        self.path = path
        self.query_string = query_string
        self.headers = headers
        self.wsgi_version = "1.0"
        self.wsgi_url_scheme = "http"

class WSGIHandler:
    def __init__(self, app):
        self.app = app
    
    def handle(self, client_sock):
        try:
            data = client_sock.recv(4096).decode()
            if not data:
                return
            lines = data.split('\r\n')
            request_line = lines[0].split()
            if len(request_line) < 2:
                return
            method = request_line[0]
            path = request_line[1].split('?')[0]
            query_string = request_line[1].split('?')[1] if '?' in request_line[1] else ''
            headers = {}
            for line in lines[1:]:
                if ':' in line:
                    key, value = line.split(':', 1)
                    headers[key.strip()] = value.strip()
            environ = WSGIEnvironment(method, path, query_string, headers)
            start_response_called = [False]
            response_body = StringIO()
            
            def start_response(status, response_headers):
                start_response_called[0] = True
                return lambda data: response_body.write(data.decode() if isinstance(data, bytes) else data)
            
            result = self.app(environ, start_response)
            response = f"HTTP/1.1 {200 if start_response_called[0] else 500} OK\r\n"
            response += f"Content-Length: {response_body.tell()}\r\n"
            response += "Content-Type: text/html\r\n\r\n"
            response += response_body.getvalue()
            client_sock.sendall(response.encode())
        finally:
            client_sock.close()

def simple_app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/html')]
    start_response(status, response_headers)
    return [b"<h1>Hello WSGI!</h1>"]

def main():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(('0.0.0.0', 8888))
    server_sock.listen(1)
    handler = WSGIHandler(simple_app)
    print("WSGI服务器运行在 http://localhost:8888")
    client_sock, addr = server_sock.accept()
    handler.handle(client_sock)


if __name__ == "__main__":
    main()
