# -----------------------------
# 题目：实现REST客户端。
# -----------------------------

import json
import urllib.request
import urllib.parse

class RestClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.headers = {"Content-Type": "application/json"}
    
    def request(self, method, path, data=None):
        url = f"{self.base_url}/{path.lstrip('/')}"
        
        body = json.dumps(data).encode('utf-8') if data else None
        
        req = urllib.request.Request(url, data=body, headers=self.headers, method=method)
        
        try:
            with urllib.request.urlopen(req) as response:
                return {
                    "status": response.status,
                    "data": json.loads(response.read().decode('utf-8'))
                }
        except urllib.error.HTTPError as e:
            return {
                "status": e.code,
                "error": e.read().decode('utf-8')
            }
    
    def get(self, path):
        return self.request("GET", path)
    
    def post(self, path, data):
        return self.request("POST", path, data)
    
    def put(self, path, data):
        return self.request("PUT", path, data)
    
    def delete(self, path):
        return self.request("DELETE", path)

if __name__ == "__main__":
    client = RestClient("https://jsonplaceholder.typicode.com")
    
    response = client.get("/posts/1")
    print(f"GET /posts/1: {response}")
    
    response = client.post("/posts", {"title": "Test", "body": "Content", "userId": 1})
    print(f"POST /posts: {response}")
