# -----------------------------
# 题目：实现WebSocket服务器。
# -----------------------------

import socket
import struct
import threading
import hashlib
import base64
import json

class WebSocketHandler:
    def __init__(self, socket, address):
        self.socket = socket
        self.address = address
        self.running = True
    
    def handshake(self):
        data = self.socket.recv(1024).decode('utf-8')
        if not data:
            return False
        
        lines = data.split('\r\n')
        key = None
        for line in lines:
            if line.startswith('Sec-WebSocket-Key:'):
                key = line.split(':')[1].strip()
                break
        
        if not key:
            return False
        
        magic = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        accept = base64.b64encode(hashlib.sha1((key + magic).encode()).digest()).decode()
        
        response = "HTTP/1.1 101 Switching Protocols\r\n"
        response += "Upgrade: websocket\r\n"
        response += "Connection: Upgrade\r\n"
        response += f"Sec-WebSocket-Accept: {accept}\r\n\r\n"
        
        self.socket.sendall(response.encode())
        return True
    
    def recv_frame(self):
        data = self.socket.recv(2)
        if len(data) < 2:
            return None
        
        first_byte, second_byte = struct.unpack('!BB', data)
        opcode = first_byte & 0x0f
        masked = (second_byte & 0x80) != 0
        payload_length = second_byte & 0x7f
        
        if payload_length == 126:
            payload_length = struct.unpack('!H', self.socket.recv(2))[0]
        elif payload_length == 127:
            payload_length = struct.unpack('!Q', self.socket.recv(8))[0]
        
        mask = self.socket.recv(4) if masked else None
        payload = self.socket.recv(payload_length)
        
        if masked:
            payload = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        
        return payload.decode('utf-8') if opcode == 1 else payload
    
    def send_message(self, message):
        if isinstance(message, str):
            data = message.encode('utf-8')
        else:
            data = message
        
        length = len(data)
        frame = bytearray()
        frame.append(0x81)
        
        if length <= 125:
            frame.append(length)
        elif length <= 65535:
            frame.append(126)
            frame.extend(struct.pack('!H', length))
        else:
            frame.append(127)
            frame.extend(struct.pack('!Q', length))
        
        frame.extend(data)
        self.socket.sendall(frame)
    
    def handle(self):
        if not self.handshake():
            return
        
        while self.running:
            try:
                message = self.recv_frame()
                if not message:
                    break
                print(f"Received: {message}")
                self.send_message(f"Echo: {message}")
            except Exception as e:
                print(f"Error: {e}")
                break
        
        self.socket.close()

class WebSocketServer:
    def __init__(self, host='127.0.0.1', port=8080):
        self.host = host
        self.port = port
        self.server_socket = None
    
    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"WebSocket server running on ws://{self.host}:{self.port}")
        
        while True:
            client_socket, address = self.server_socket.accept()
            handler = WebSocketHandler(client_socket, address)
            threading.Thread(target=handler.handle, daemon=True).start()

if __name__ == "__main__":
    server = WebSocketServer()
    server.start()
