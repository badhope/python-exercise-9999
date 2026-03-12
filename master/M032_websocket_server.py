# -----------------------------
# 题目：实现WebSocket服务器。
# 描述：支持连接管理、消息广播、房间功能。
# -----------------------------

import socket
import hashlib
import base64
import struct
import threading
import json
from typing import Dict, List, Set, Callable, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

class OpCode(Enum):
    CONTINUATION = 0x0
    TEXT = 0x1
    BINARY = 0x2
    CLOSE = 0x8
    PING = 0x9
    PONG = 0xA

@dataclass
class WebSocketMessage:
    opcode: OpCode
    payload: bytes
    fin: bool = True

@dataclass
class WebSocketConnection:
    conn_id: str
    socket: socket.socket
    address: tuple
    rooms: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_alive: bool = True

class WebSocketFrame:
    @staticmethod
    def parse(data: bytes) -> WebSocketMessage:
        if len(data) < 2:
            return None
        
        fin = (data[0] & 0x80) >> 7
        opcode = OpCode(data[0] & 0x0F)
        
        masked = (data[1] & 0x80) >> 7
        payload_len = data[1] & 0x7F
        
        offset = 2
        
        if payload_len == 126:
            payload_len = struct.unpack('>H', data[2:4])[0]
            offset = 4
        elif payload_len == 127:
            payload_len = struct.unpack('>Q', data[2:10])[0]
            offset = 10
        
        if masked:
            mask_key = data[offset:offset+4]
            offset += 4
            
            payload = bytearray(data[offset:offset+payload_len])
            for i in range(len(payload)):
                payload[i] ^= mask_key[i % 4]
            payload = bytes(payload)
        else:
            payload = data[offset:offset+payload_len]
        
        return WebSocketMessage(opcode=opcode, payload=payload, fin=bool(fin))
    
    @staticmethod
    def build(message: WebSocketMessage) -> bytes:
        frame = bytearray()
        
        first_byte = (0x80 if message.fin else 0x00) | message.opcode.value
        frame.append(first_byte)
        
        payload_len = len(message.payload)
        
        if payload_len <= 125:
            frame.append(payload_len)
        elif payload_len <= 65535:
            frame.append(126)
            frame.extend(struct.pack('>H', payload_len))
        else:
            frame.append(127)
            frame.extend(struct.pack('>Q', payload_len))
        
        frame.extend(message.payload)
        
        return bytes(frame)

class WebSocketServer:
    def __init__(self, host: str = 'localhost', port: int = 8765):
        self.host = host
        self.port = port
        self.connections: Dict[str, WebSocketConnection] = {}
        self.rooms: Dict[str, Set[str]] = {}
        self._lock = threading.Lock()
        self._running = False
        self._server_socket: Optional[socket.socket] = None
        self._conn_counter = 0
        
        self.on_connect: Callable[[WebSocketConnection], None] = None
        self.on_disconnect: Callable[[WebSocketConnection], None] = None
        self.on_message: Callable[[WebSocketConnection, str], None] = None
    
    def _generate_conn_id(self) -> str:
        with self._lock:
            self._conn_counter += 1
            return f"conn-{self._conn_counter}"
    
    def _handshake(self, client_socket: socket.socket, request: str) -> bool:
        try:
            lines = request.split('\r\n')
            headers = {}
            
            for line in lines[1:]:
                if ':' in line:
                    key, value = line.split(':', 1)
                    headers[key.strip().lower()] = value.strip()
            
            if 'upgrade' not in headers.get('upgrade', '').lower():
                return False
            
            key = headers.get('sec-websocket-key', '')
            if not key:
                return False
            
            accept_key = base64.b64encode(
                hashlib.sha1((key + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode()).digest()
            ).decode()
            
            response = (
                'HTTP/1.1 101 Switching Protocols\r\n'
                'Upgrade: websocket\r\n'
                'Connection: Upgrade\r\n'
                f'Sec-WebSocket-Accept: {accept_key}\r\n'
                '\r\n'
            )
            
            client_socket.send(response.encode())
            return True
        
        except Exception:
            return False
    
    def _handle_client(self, client_socket: socket.socket, address: tuple):
        conn_id = self._generate_conn_id()
        connection = WebSocketConnection(
            conn_id=conn_id,
            socket=client_socket,
            address=address
        )
        
        try:
            request = client_socket.recv(4096).decode()
            
            if not self._handshake(client_socket, request):
                client_socket.close()
                return
            
            with self._lock:
                self.connections[conn_id] = connection
            
            if self.on_connect:
                self.on_connect(connection)
            
            while self._running and connection.is_alive:
                try:
                    data = client_socket.recv(4096)
                    if not data:
                        break
                    
                    message = WebSocketFrame.parse(data)
                    if message is None:
                        continue
                    
                    if message.opcode == OpCode.CLOSE:
                        break
                    elif message.opcode == OpCode.PING:
                        pong = WebSocketMessage(OpCode.PONG, message.payload)
                        client_socket.send(WebSocketFrame.build(pong))
                    elif message.opcode == OpCode.TEXT:
                        text = message.payload.decode('utf-8')
                        if self.on_message:
                            self.on_message(connection, text)
                
                except Exception:
                    break
        
        finally:
            with self._lock:
                if conn_id in self.connections:
                    del self.connections[conn_id]
                
                for room in connection.rooms:
                    if room in self.rooms:
                        self.rooms[room].discard(conn_id)
            
            if self.on_disconnect:
                self.on_disconnect(connection)
            
            try:
                client_socket.close()
            except:
                pass
    
    def start(self):
        self._running = True
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind((self.host, self.port))
        self._server_socket.listen(5)
        
        print(f"WebSocket服务器启动: ws://{self.host}:{self.port}")
        
        while self._running:
            try:
                client_socket, address = self._server_socket.accept()
                thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, address)
                )
                thread.daemon = True
                thread.start()
            except Exception:
                break
    
    def stop(self):
        self._running = False
        if self._server_socket:
            self._server_socket.close()
    
    def send(self, connection: WebSocketConnection, message: str):
        if not connection.is_alive:
            return
        
        msg = WebSocketMessage(OpCode.TEXT, message.encode('utf-8'))
        try:
            connection.socket.send(WebSocketFrame.build(msg))
        except:
            connection.is_alive = False
    
    def broadcast(self, message: str, room: str = None):
        with self._lock:
            if room:
                conn_ids = self.rooms.get(room, set())
                connections = [self.connections[cid] for cid in conn_ids if cid in self.connections]
            else:
                connections = list(self.connections.values())
        
        for conn in connections:
            self.send(conn, message)
    
    def join_room(self, connection: WebSocketConnection, room: str):
        with self._lock:
            connection.rooms.add(room)
            if room not in self.rooms:
                self.rooms[room] = set()
            self.rooms[room].add(connection.conn_id)
    
    def leave_room(self, connection: WebSocketConnection, room: str):
        with self._lock:
            connection.rooms.discard(room)
            if room in self.rooms:
                self.rooms[room].discard(connection.conn_id)
    
    def get_connections(self) -> List[WebSocketConnection]:
        with self._lock:
            return list(self.connections.values())

def main():
    server = WebSocketServer('localhost', 8765)
    
    def on_connect(conn):
        print(f"客户端连接: {conn.conn_id}")
        server.send(conn, json.dumps({'type': 'welcome', 'conn_id': conn.conn_id}))
    
    def on_disconnect(conn):
        print(f"客户端断开: {conn.conn_id}")
    
    def on_message(conn, message):
        print(f"收到消息: {message}")
        data = json.loads(message)
        
        if data.get('type') == 'join':
            server.join_room(conn, data['room'])
            server.broadcast(json.dumps({
                'type': 'joined',
                'conn_id': conn.conn_id,
                'room': data['room']
            }), data['room'])
        elif data.get('type') == 'chat':
            server.broadcast(json.dumps({
                'type': 'chat',
                'conn_id': conn.conn_id,
                'message': data['message']
            }), data.get('room'))
    
    server.on_connect = on_connect
    server.on_disconnect = on_disconnect
    server.on_message = on_message
    
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()

if __name__ == "__main__":
    main()
