# -----------------------------
# 题目：实现RPC框架。
# -----------------------------

import socket
import pickle
import threading
import uuid

class RPCRequest:
    def __init__(self, method, args, kwargs, request_id):
        self.method = method
        self.args = args
        self.kwargs = kwargs
        self.request_id = request_id

class RPCResponse:
    def __init__(self, request_id, result=None, error=None):
        self.request_id = request_id
        self.result = result
        self.error = error

class RPCServer:
    def __init__(self, host='127.0.0.1', port=9000):
        self.host = host
        self.port = port
        self.server_socket = None
        self.handlers = {}
    
    def register(self, name, func):
        self.handlers[name] = func
    
    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"RPC Server running on {self.host}:{self.port}")
        
        while True:
            client_socket, _ = self.server_socket.accept()
            threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()
    
    def handle_client(self, client_socket):
        try:
            data = b''
            while True:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                data += chunk
                if len(chunk) < 4096:
                    break
            
            if not data:
                return
            
            request = pickle.loads(data)
            
            if request.method in self.handlers:
                result = self.handlers[request.method](*request.args, **request.kwargs)
                response = RPCResponse(request.request_id, result=result)
            else:
                response = RPCResponse(request.request_id, error=f"Method {request.method} not found")
            
            client_socket.sendall(pickle.dumps(response))
        except Exception as e:
            print(f"Error: {e}")
        finally:
            client_socket.close()

class RPCClient:
    def __init__(self, host='127.0.0.1', port=9000):
        self.host = host
        self.port = port
    
    def call(self, method, *args, **kwargs):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        
        request = RPCRequest(method, args, kwargs, str(uuid.uuid4()))
        sock.sendall(pickle.dumps(request))
        
        data = sock.recv(4096)
        sock.close()
        
        response = pickle.loads(data)
        if response.error:
            raise Exception(response.error)
        return response.result
    
    def __getattr__(self, name):
        def wrapper(*args, **kwargs):
            return self.call(name, *args, **kwargs)
        return wrapper

def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

if __name__ == "__main__":
    server = RPCServer()
    server.register("add", add)
    server.register("multiply", multiply)
    
    client = RPCClient()
    print(f"add(2, 3) = {client.add(2, 3)}")
    print(f"multiply(4, 5) = {client.multiply(4, 5)}")
