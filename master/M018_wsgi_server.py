# -----------------------------
# 题目：实现WSGI服务器。
# -----------------------------

class WSGIHandler:
    def __init__(self, app):
        self.app = app
    
    def handle(self, environ, start_response):
        response_body = self.app(environ, start_response)
        return response_body
    
    def serve(self, host='127.0.0.1', port=8000):
        import socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen(5)
        print(f"WSGI Server running on http://{host}:{port}")
        
        while True:
            client_socket, address = server_socket.accept()
            self._handle_request(client_socket)
    
    def _handle_request(self, client_socket):
        import io
        request = client_socket.recv(1024).decode('utf-8')
        if not request:
            client_socket.close()
            return
        
        lines = request.split('\r\n')
        if not lines:
            client_socket.close()
            return
        
        method, path, _ = lines[0].split()
        environ = {
            'REQUEST_METHOD': method,
            'PATH_INFO': path,
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'http',
            'wsgi.input': io.StringIO(''),
            'wsgi.errors': io.StringIO(),
        }
        
        def start_response(status, response_headers):
            response = f"HTTP/1.1 {status}\r\n"
            for header in response_headers:
                response += f"{header[0]}: {header[1]}\r\n"
            response += "\r\n"
            client_socket.sendall(response.encode('utf-8'))
        
        response_body = self.app(environ, start_response)
        for chunk in response_body:
            client_socket.sendall(chunk)
        
        client_socket.close()

def simple_app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-Type', 'text/plain')]
    start_response(status, response_headers)
    return [b'Hello from WSGI!']

if __name__ == "__main__":
    handler = WSGIHandler(simple_app)
    handler.serve()
