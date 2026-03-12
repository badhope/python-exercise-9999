# -----------------------------
# 题目：实现简单的URL解析器。
# 描述：解析URL的各个组成部分。
# -----------------------------

import re
from urllib.parse import parse_qs, urlparse

class URLParser:
    def __init__(self, url):
        self.url = url
        self.parsed = urlparse(url)
    
    def get_scheme(self):
        return self.parsed.scheme
    
    def get_host(self):
        return self.parsed.netloc
    
    def get_port(self):
        if ':' in self.parsed.netloc:
            return int(self.parsed.netloc.split(':')[1])
        if self.parsed.scheme == 'https':
            return 443
        if self.parsed.scheme == 'http':
            return 80
        return None
    
    def get_path(self):
        return self.parsed.path
    
    def get_query(self):
        return self.parsed.query
    
    def get_query_params(self):
        return parse_qs(self.parsed.query)
    
    def get_fragment(self):
        return self.parsed.fragment
    
    def get_domain(self):
        host = self.get_host()
        if ':' in host:
            host = host.split(':')[0]
        parts = host.split('.')
        if len(parts) >= 2:
            return '.'.join(parts[-2:])
        return host
    
    def get_subdomain(self):
        host = self.get_host()
        if ':' in host:
            host = host.split(':')[0]
        parts = host.split('.')
        if len(parts) > 2:
            return '.'.join(parts[:-2])
        return None
    
    def is_secure(self):
        return self.parsed.scheme == 'https'
    
    def get_all_info(self):
        return {
            "完整URL": self.url,
            "协议": self.get_scheme(),
            "主机": self.get_host(),
            "端口": self.get_port(),
            "路径": self.get_path(),
            "查询字符串": self.get_query(),
            "查询参数": self.get_query_params(),
            "锚点": self.get_fragment(),
            "域名": self.get_domain(),
            "子域名": self.get_subdomain(),
            "是否安全": self.is_secure()
        }

def main():
    url = "https://www.example.com:8080/path/to/page?name=test&id=123#section1"
    
    parser = URLParser(url)
    info = parser.get_all_info()
    
    print("URL解析结果:")
    for key, value in info.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
