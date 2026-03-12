# -----------------------------
# 题目：实现简单的REST客户端。
# -----------------------------

import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"

@dataclass
class Response:
    status_code: int
    headers: Dict[str, str]
    body: Any
    ok: bool
    
    def json(self) -> Any:
        if isinstance(self.body, str):
            return json.loads(self.body)
        return self.body
    
    def text(self) -> str:
        return str(self.body) if self.body else ""

class RESTClient:
    def __init__(self, base_url: str = "", default_headers: Dict[str, str] = None):
        self.base_url = base_url.rstrip('/')
        self.default_headers = default_headers or {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self.timeout = 30
    
    def get(self, endpoint: str, params: Dict = None, headers: Dict = None) -> Response:
        return self._request(HttpMethod.GET, endpoint, params=params, headers=headers)
    
    def post(self, endpoint: str, data: Any = None, headers: Dict = None) -> Response:
        return self._request(HttpMethod.POST, endpoint, data=data, headers=headers)
    
    def put(self, endpoint: str, data: Any = None, headers: Dict = None) -> Response:
        return self._request(HttpMethod.PUT, endpoint, data=data, headers=headers)
    
    def delete(self, endpoint: str, headers: Dict = None) -> Response:
        return self._request(HttpMethod.DELETE, endpoint, headers=headers)
    
    def patch(self, endpoint: str, data: Any = None, headers: Dict = None) -> Response:
        return self._request(HttpMethod.PATCH, endpoint, data=data, headers=headers)
    
    def _request(self, method: HttpMethod, endpoint: str, 
                 params: Dict = None, data: Any = None, headers: Dict = None) -> Response:
        url = self._build_url(endpoint, params)
        merged_headers = {**self.default_headers, **(headers or {})}
        
        return self._mock_request(method, url, merged_headers, data)
    
    def _build_url(self, endpoint: str, params: Dict = None) -> str:
        url = f"{self.base_url}{endpoint}" if self.base_url else endpoint
        
        if params:
            query = '&'.join(f"{k}={v}" for k, v in params.items())
            url = f"{url}?{query}"
        
        return url
    
    def _mock_request(self, method: HttpMethod, url: str, 
                      headers: Dict, data: Any) -> Response:
        return Response(
            status_code=200,
            headers={'Content-Type': 'application/json'},
            body={'method': method.value, 'url': url, 'data': data},
            ok=True
        )

class Resource:
    def __init__(self, client: RESTClient, name: str):
        self.client = client
        self.name = name
    
    def list(self, params: Dict = None) -> Response:
        return self.client.get(f"/{self.name}", params=params)
    
    def get(self, id: int) -> Response:
        return self.client.get(f"/{self.name}/{id}")
    
    def create(self, data: Dict) -> Response:
        return self.client.post(f"/{self.name}", data=data)
    
    def update(self, id: int, data: Dict) -> Response:
        return self.client.put(f"/{self.name}/{id}", data=data)
    
    def delete(self, id: int) -> Response:
        return self.client.delete(f"/{self.name}/{id}")

class APIClient:
    def __init__(self, base_url: str):
        self.client = RESTClient(base_url)
        self._resources: Dict[str, Resource] = {}
    
    def resource(self, name: str) -> Resource:
        if name not in self._resources:
            self._resources[name] = Resource(self.client, name)
        return self._resources[name]
    
    def authenticate(self, token: str):
        self.client.default_headers['Authorization'] = f'Bearer {token}'
    
    def set_timeout(self, timeout: int):
        self.client.timeout = timeout

class RequestBuilder:
    def __init__(self, client: RESTClient):
        self.client = client
        self._method = HttpMethod.GET
        self._endpoint = ""
        self._params: Dict = {}
        self._data: Any = None
        self._headers: Dict = {}
    
    def method(self, method: HttpMethod) -> 'RequestBuilder':
        self._method = method
        return self
    
    def endpoint(self, endpoint: str) -> 'RequestBuilder':
        self._endpoint = endpoint
        return self
    
    def param(self, key: str, value: Any) -> 'RequestBuilder':
        self._params[key] = value
        return self
    
    def data(self, data: Any) -> 'RequestBuilder':
        self._data = data
        return self
    
    def header(self, key: str, value: str) -> 'RequestBuilder':
        self._headers[key] = value
        return self
    
    def execute(self) -> Response:
        return self.client._request(
            self._method, 
            self._endpoint,
            params=self._params if self._params else None,
            data=self._data,
            headers=self._headers if self._headers else None
        )

def main():
    client = RESTClient("https://api.example.com")
    
    print("=== GET请求 ===")
    response = client.get("/users", params={'page': 1, 'limit': 10})
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    
    print("\n=== POST请求 ===")
    response = client.post("/users", data={'name': '张三', 'email': 'zhang@example.com'})
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    
    print("\n=== 使用Resource ===")
    api = APIClient("https://api.example.com")
    users = api.resource("users")
    
    response = users.list({'status': 'active'})
    print(f"用户列表: {response.json()}")
    
    response = users.get(1)
    print(f"获取用户: {response.json()}")
    
    print("\n=== 使用RequestBuilder ===")
    builder = RequestBuilder(client)
    response = (builder
                .method(HttpMethod.POST)
                .endpoint("/orders")
                .data({'product_id': 1, 'quantity': 2})
                .header('X-Custom', 'value')
                .execute())
    print(f"构建请求: {response.json()}")


if __name__ == "__main__":
    main()
