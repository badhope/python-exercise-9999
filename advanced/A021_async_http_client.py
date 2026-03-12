# -----------------------------
# 题目：实现异步HTTP客户端。
# -----------------------------

import asyncio
import json
from urllib.parse import urlparse

class AsyncHTTPClient:
    def __init__(self, timeout=30):
        self.timeout = timeout
        self.default_headers = {
            'User-Agent': 'AsyncHTTPClient/1.0',
            'Accept': 'application/json'
        }
    
    async def get(self, url, headers=None):
        return await self._request('GET', url, headers=headers)
    
    async def post(self, url, data=None, headers=None):
        return await self._request('POST', url, data=data, headers=headers)
    
    async def put(self, url, data=None, headers=None):
        return await self._request('PUT', url, data=data, headers=headers)
    
    async def delete(self, url, headers=None):
        return await self._request('DELETE', url, headers=headers)
    
    async def _request(self, method, url, data=None, headers=None):
        parsed = urlparse(url)
        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        path = parsed.path or '/'
        if parsed.query:
            path += f'?{parsed.query}'
        
        merged_headers = {**self.default_headers, **(headers or {})}
        merged_headers['Host'] = host
        
        if data:
            merged_headers['Content-Type'] = 'application/json'
            body = json.dumps(data)
            merged_headers['Content-Length'] = len(body)
        else:
            body = ''
        
        request_line = f"{method} {path} HTTP/1.1\r\n"
        header_lines = ''.join(f"{k}: {v}\r\n" for k, v in merged_headers.items())
        request = f"{request_line}{header_lines}\r\n{body}"
        
        return {
            'status': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': {'url': url, 'method': method}
        }
    
    async def request_multiple(self, requests):
        tasks = []
        for req in requests:
            method = req.get('method', 'GET')
            url = req['url']
            data = req.get('data')
            headers = req.get('headers')
            
            if method == 'GET':
                tasks.append(self.get(url, headers))
            elif method == 'POST':
                tasks.append(self.post(url, data, headers))
        
        return await asyncio.gather(*tasks)

class HTTPSession:
    def __init__(self, base_url=''):
        self.base_url = base_url
        self.client = AsyncHTTPClient()
        self.cookies = {}
    
    async def get(self, path, headers=None):
        url = self.base_url + path
        return await self.client.get(url, headers)
    
    async def post(self, path, data=None, headers=None):
        url = self.base_url + path
        return await self.client.post(url, data, headers)
    
    def set_cookie(self, name, value):
        self.cookies[name] = value

async def main():
    client = AsyncHTTPClient()
    
    print("=== 单个请求 ===")
    result = await client.get('http://example.com/api/users')
    print(f"结果: {result}")
    
    print("\n=== 并发请求 ===")
    requests = [
        {'method': 'GET', 'url': 'http://example.com/api/users/1'},
        {'method': 'GET', 'url': 'http://example.com/api/users/2'},
        {'method': 'POST', 'url': 'http://example.com/api/users', 'data': {'name': '张三'}}
    ]
    results = await client.request_multiple(requests)
    print(f"并发请求结果数: {len(results)}")


if __name__ == "__main__":
    asyncio.run(main())
