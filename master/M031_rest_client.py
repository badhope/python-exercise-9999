# -----------------------------
# 题目：实现REST客户端。
# 描述：支持HTTP方法、请求拦截器、响应处理。
# -----------------------------

import json
import time
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from urllib.parse import urlencode

class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"

@dataclass
class Request:
    method: HttpMethod
    url: str
    headers: Dict[str, str] = field(default_factory=dict)
    params: Dict[str, Any] = field(default_factory=dict)
    body: Any = None
    timeout: float = 30.0

@dataclass
class Response:
    status_code: int
    headers: Dict[str, str]
    body: Any
    elapsed: float

class RequestInterceptor:
    def before_request(self, request: Request) -> Request:
        return request
    
    def after_response(self, response: Response) -> Response:
        return response

class AuthInterceptor(RequestInterceptor):
    def __init__(self, token: str, token_type: str = "Bearer"):
        self.token = token
        self.token_type = token_type
    
    def before_request(self, request: Request) -> Request:
        request.headers['Authorization'] = f"{self.token_type} {self.token}"
        return request

class LoggingInterceptor(RequestInterceptor):
    def before_request(self, request: Request) -> Request:
        print(f"[请求] {request.method.value} {request.url}")
        return request
    
    def after_response(self, response: Response) -> Response:
        print(f"[响应] 状态码: {response.status_code}, 耗时: {response.elapsed:.3f}s")
        return response

class RetryInterceptor(RequestInterceptor):
    def __init__(self, max_retries: int = 3, retry_status_codes: List[int] = None):
        self.max_retries = max_retries
        self.retry_status_codes = retry_status_codes or [500, 502, 503, 504]
        self._client = None
    
    def set_client(self, client: 'RestClient'):
        self._client = client
    
    def after_response(self, response: Response) -> Response:
        return response

class RestClient:
    def __init__(self, base_url: str = ""):
        self.base_url = base_url.rstrip('/')
        self.interceptors: List[RequestInterceptor] = []
        self.default_headers: Dict[str, str] = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def add_interceptor(self, interceptor: RequestInterceptor) -> 'RestClient':
        self.interceptors.append(interceptor)
        if isinstance(interceptor, RetryInterceptor):
            interceptor.set_client(self)
        return self
    
    def set_default_header(self, key: str, value: str) -> 'RestClient':
        self.default_headers[key] = value
        return self
    
    def _build_url(self, path: str, params: Dict[str, Any] = None) -> str:
        url = f"{self.base_url}{path}" if self.base_url else path
        
        if params:
            query_string = urlencode(params)
            url = f"{url}?{query_string}"
        
        return url
    
    def request(self, request: Request) -> Response:
        for interceptor in self.interceptors:
            request = interceptor.before_request(request)
        
        start_time = time.time()
        
        url = self._build_url(request.url, request.params)
        
        headers = {**self.default_headers, **request.headers}
        
        body_data = None
        if request.body:
            if isinstance(request.body, (dict, list)):
                body_data = json.dumps(request.body).encode('utf-8')
            elif isinstance(request.body, str):
                body_data = request.body.encode('utf-8')
        
        req = urllib.request.Request(
            url,
            data=body_data,
            headers=headers,
            method=request.method.value
        )
        
        try:
            with urllib.request.urlopen(req, timeout=request.timeout) as response:
                response_body = response.read().decode('utf-8')
                
                try:
                    response_body = json.loads(response_body)
                except json.JSONDecodeError:
                    pass
                
                result = Response(
                    status_code=response.status,
                    headers=dict(response.headers),
                    body=response_body,
                    elapsed=time.time() - start_time
                )
        
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else ""
            result = Response(
                status_code=e.code,
                headers=dict(e.headers) if e.headers else {},
                body=error_body,
                elapsed=time.time() - start_time
            )
        
        except urllib.error.URLError as e:
            result = Response(
                status_code=0,
                headers={},
                body=str(e.reason),
                elapsed=time.time() - start_time
            )
        
        for interceptor in reversed(self.interceptors):
            result = interceptor.after_response(result)
        
        return result
    
    def get(self, path: str, params: Dict[str, Any] = None, **kwargs) -> Response:
        request = Request(
            method=HttpMethod.GET,
            url=path,
            params=params,
            **kwargs
        )
        return self.request(request)
    
    def post(self, path: str, body: Any = None, **kwargs) -> Response:
        request = Request(
            method=HttpMethod.POST,
            url=path,
            body=body,
            **kwargs
        )
        return self.request(request)
    
    def put(self, path: str, body: Any = None, **kwargs) -> Response:
        request = Request(
            method=HttpMethod.PUT,
            url=path,
            body=body,
            **kwargs
        )
        return self.request(request)
    
    def delete(self, path: str, **kwargs) -> Response:
        request = Request(
            method=HttpMethod.DELETE,
            url=path,
            **kwargs
        )
        return self.request(request)
    
    def patch(self, path: str, body: Any = None, **kwargs) -> Response:
        request = Request(
            method=HttpMethod.PATCH,
            url=path,
            body=body,
            **kwargs
        )
        return self.request(request)

class Resource:
    def __init__(self, client: RestClient, path: str):
        self.client = client
        self.path = path
    
    def list(self, params: Dict[str, Any] = None) -> Response:
        return self.client.get(self.path, params=params)
    
    def get(self, resource_id: Any) -> Response:
        return self.client.get(f"{self.path}/{resource_id}")
    
    def create(self, data: Dict[str, Any]) -> Response:
        return self.client.post(self.path, body=data)
    
    def update(self, resource_id: Any, data: Dict[str, Any]) -> Response:
        return self.client.put(f"{self.path}/{resource_id}", body=data)
    
    def delete(self, resource_id: Any) -> Response:
        return self.client.delete(f"{self.path}/{resource_id}")

def main():
    client = RestClient("https://jsonplaceholder.typicode.com")
    client.add_interceptor(LoggingInterceptor())
    
    response = client.get("/posts/1")
    print(f"状态码: {response.status_code}")
    print(f"响应体: {response.body}")
    
    response = client.get("/posts", params={"userId": 1, "_limit": 3})
    print(f"\n文章列表: {len(response.body) if isinstance(response.body, list) else response.body}")
    
    response = client.post("/posts", body={
        "title": "测试文章",
        "body": "这是文章内容",
        "userId": 1
    })
    print(f"\n创建文章: {response.status_code}")

if __name__ == "__main__":
    main()
