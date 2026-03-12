# -----------------------------
# 题目：实现RPC框架。
# 描述：支持远程方法调用、序列化、服务注册。
# -----------------------------

import socket
import pickle
import threading
import json
from typing import Dict, Any, Callable, Optional, Type
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class RPCRequest:
    request_id: str
    service_name: str
    method_name: str
    args: tuple
    kwargs: dict

@dataclass
class RPCResponse:
    request_id: str
    success: bool
    result: Any = None
    error: str = None

class Serializer(ABC):
    @abstractmethod
    def serialize(self, obj: Any) -> bytes:
        pass
    
    @abstractmethod
    def deserialize(self, data: bytes) -> Any:
        pass

class PickleSerializer(Serializer):
    def serialize(self, obj: Any) -> bytes:
        return pickle.dumps(obj)
    
    def deserialize(self, data: bytes) -> Any:
        return pickle.loads(data)

class JSONSerializer(Serializer):
    def serialize(self, obj: Any) -> bytes:
        return json.dumps(obj, default=str).encode('utf-8')
    
    def deserialize(self, data: bytes) -> Any:
        return json.loads(data.decode('utf-8'))

class ServiceRegistry:
    def __init__(self):
        self._services: Dict[str, Dict[str, Callable]] = {}
    
    def register(self, service_name: str, instance: Any):
        methods = {}
        for attr_name in dir(instance):
            if not attr_name.startswith('_'):
                attr = getattr(instance, attr_name)
                if callable(attr):
                    methods[attr_name] = attr
        
        self._services[service_name] = methods
    
    def get_method(self, service_name: str, method_name: str) -> Optional[Callable]:
        service = self._services.get(service_name)
        if service:
            return service.get(method_name)
        return None
    
    def list_services(self) -> Dict[str, List[str]]:
        return {
            name: list(methods.keys())
            for name, methods in self._services.items()
        }

class RPCServer:
    def __init__(self, host: str = 'localhost', port: int = 9000, serializer: Serializer = None):
        self.host = host
        self.port = port
        self.serializer = serializer or PickleSerializer()
        self.registry = ServiceRegistry()
        self._running = False
        self._server_socket: Optional[socket.socket] = None
    
    def register_service(self, service_name: str, instance: Any):
        self.registry.register(service_name, instance)
    
    def start(self):
        self._running = True
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind((self.host, self.port))
        self._server_socket.listen(10)
        
        print(f"RPC服务器启动: {self.host}:{self.port}")
        print(f"已注册服务: {self.registry.list_services()}")
        
        while self._running:
            try:
                client_socket, address = self._server_socket.accept()
                thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket,)
                )
                thread.daemon = True
                thread.start()
            except Exception:
                break
    
    def stop(self):
        self._running = False
        if self._server_socket:
            self._server_socket.close()
    
    def _handle_client(self, client_socket: socket.socket):
        try:
            while self._running:
                data = self._recv_all(client_socket)
                if not data:
                    break
                
                request = self.serializer.deserialize(data)
                response = self._process_request(request)
                
                response_data = self.serializer.serialize(response)
                self._send_all(client_socket, response_data)
        
        except Exception as e:
            pass
        finally:
            client_socket.close()
    
    def _process_request(self, request: RPCRequest) -> RPCResponse:
        method = self.registry.get_method(request.service_name, request.method_name)
        
        if method is None:
            return RPCResponse(
                request_id=request.request_id,
                success=False,
                error=f"方法未找到: {request.service_name}.{request.method_name}"
            )
        
        try:
            result = method(*request.args, **request.kwargs)
            return RPCResponse(
                request_id=request.request_id,
                success=True,
                result=result
            )
        except Exception as e:
            return RPCResponse(
                request_id=request.request_id,
                success=False,
                error=str(e)
            )
    
    def _recv_all(self, sock: socket.socket) -> bytes:
        length_data = sock.recv(4)
        if not length_data:
            return None
        
        length = int.from_bytes(length_data, 'big')
        data = b''
        while len(data) < length:
            chunk = sock.recv(min(length - len(data), 4096))
            if not chunk:
                return None
            data += chunk
        
        return data
    
    def _send_all(self, sock: socket.socket, data: bytes):
        length = len(data)
        sock.sendall(length.to_bytes(4, 'big') + data)

class RPCClient:
    def __init__(self, host: str = 'localhost', port: int = 9000, serializer: Serializer = None):
        self.host = host
        self.port = port
        self.serializer = serializer or PickleSerializer()
        self._request_counter = 0
    
    def _generate_request_id(self) -> str:
        self._request_counter += 1
        return f"req-{self._request_counter}"
    
    def call(self, service_name: str, method_name: str, *args, **kwargs) -> Any:
        request = RPCRequest(
            request_id=self._generate_request_id(),
            service_name=service_name,
            method_name=method_name,
            args=args,
            kwargs=kwargs
        )
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((self.host, self.port))
            
            request_data = self.serializer.serialize(request)
            self._send_all(sock, request_data)
            
            response_data = self._recv_all(sock)
            response = self.serializer.deserialize(response_data)
            
            if not response.success:
                raise Exception(response.error)
            
            return response.result
        
        finally:
            sock.close()
    
    def get_proxy(self, service_name: str) -> 'ServiceProxy':
        return ServiceProxy(self, service_name)
    
    def _recv_all(self, sock: socket.socket) -> bytes:
        length_data = sock.recv(4)
        if not length_data:
            return None
        
        length = int.from_bytes(length_data, 'big')
        data = b''
        while len(data) < length:
            chunk = sock.recv(min(length - len(data), 4096))
            if not chunk:
                return None
            data += chunk
        
        return data
    
    def _send_all(self, sock: socket.socket, data: bytes):
        length = len(data)
        sock.sendall(length.to_bytes(4, 'big') + data)

class ServiceProxy:
    def __init__(self, client: RPCClient, service_name: str):
        self._client = client
        self._service_name = service_name
    
    def __getattr__(self, method_name: str):
        def method(*args, **kwargs):
            return self._client.call(self._service_name, method_name, *args, **kwargs)
        return method

class CalculatorService:
    def add(self, a: int, b: int) -> int:
        return a + b
    
    def subtract(self, a: int, b: int) -> int:
        return a - b
    
    def multiply(self, a: int, b: int) -> int:
        return a * b
    
    def divide(self, a: int, b: int) -> float:
        if b == 0:
            raise ValueError("除数不能为0")
        return a / b

class UserService:
    def __init__(self):
        self.users = {
            1: {'id': 1, 'name': '张三', 'email': 'zhang@example.com'},
            2: {'id': 2, 'name': '李四', 'email': 'li@example.com'},
        }
    
    def get_user(self, user_id: int) -> dict:
        return self.users.get(user_id)
    
    def list_users(self) -> list:
        return list(self.users.values())

def main():
    server = RPCServer('localhost', 9000)
    server.register_service('calculator', CalculatorService())
    server.register_service('user', UserService())
    
    server_thread = threading.Thread(target=server.start)
    server_thread.daemon = True
    server_thread.start()
    
    import time
    time.sleep(0.5)
    
    client = RPCClient('localhost', 9000)
    
    calc = client.get_proxy('calculator')
    print(f"1 + 2 = {calc.add(1, 2)}")
    print(f"10 - 3 = {calc.subtract(10, 3)}")
    print(f"4 * 5 = {calc.multiply(4, 5)}")
    
    user = client.get_proxy('user')
    print(f"用户1: {user.get_user(1)}")
    print(f"所有用户: {user.list_users()}")
    
    server.stop()

if __name__ == "__main__":
    main()
