# -----------------------------
# 题目：HTTP客户端封装。
# 描述：使用socket实现简单的HTTP客户端。
# -----------------------------

import socket

class HTTPClient:
    def __init__(self, host, port=80):
        self.host = host
        self.port = port
    
    def get(self, path="/"):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        request = f"GET {path} HTTP/1.1\r\nHost: {self.host}\r\nConnection: close\r\n\r\n"
        sock.sendall(request.encode())
        response = b""
        while True:
            data = sock.recv(1024)
            if not data:
                break
            response += data
        sock.close()
        return response.decode('utf-8', errors='ignore')

def main():
    client = HTTPClient("example.com")
    response = client.get("/")
    print(f"状态: {response.split('\n')[0]}")


if __name__ == "__main__":
    main()
