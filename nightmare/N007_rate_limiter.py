# -----------------------------
# 题目：实现简单的分布式限流器。
# 描述：支持令牌桶、滑动窗口算法。
# -----------------------------

import time
import threading
from collections import deque

class TokenBucket:
    def __init__(self, rate, capacity):
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
        self._lock = threading.Lock()
    
    def consume(self, tokens=1):
        with self._lock:
            now = time.time()
            elapsed = now - self.last_update
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last_update = now
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def get_tokens(self):
        with self._lock:
            now = time.time()
            elapsed = now - self.last_update
            return min(self.capacity, self.tokens + elapsed * self.rate)

class SlidingWindow:
    def __init__(self, max_requests, window_size):
        self.max_requests = max_requests
        self.window_size = window_size
        self.requests = deque()
        self._lock = threading.Lock()
    
    def is_allowed(self):
        with self._lock:
            now = time.time()
            cutoff = now - self.window_size
            
            while self.requests and self.requests[0] < cutoff:
                self.requests.popleft()
            
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True
            return False
    
    def get_current_count(self):
        with self._lock:
            now = time.time()
            cutoff = now - self.window_size
            return sum(1 for t in self.requests if t >= cutoff)

class DistributedRateLimiter:
    def __init__(self, algorithm='token_bucket', **kwargs):
        self.algorithm = algorithm
        self.limiters = {}
        self._lock = threading.Lock()
        
        if algorithm == 'token_bucket':
            self.rate = kwargs.get('rate', 10)
            self.capacity = kwargs.get('capacity', 100)
        else:
            self.max_requests = kwargs.get('max_requests', 100)
            self.window_size = kwargs.get('window_size', 60)
    
    def _get_limiter(self, key):
        with self._lock:
            if key not in self.limiters:
                if self.algorithm == 'token_bucket':
                    self.limiters[key] = TokenBucket(self.rate, self.capacity)
                else:
                    self.limiters[key] = SlidingWindow(self.max_requests, self.window_size)
            return self.limiters[key]
    
    def is_allowed(self, key):
        limiter = self._get_limiter(key)
        if self.algorithm == 'token_bucket':
            return limiter.consume()
        return limiter.is_allowed()

def rate_limit(key_func=None, **limiter_kwargs):
    limiter = DistributedRateLimiter(**limiter_kwargs)
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            key = key_func(*args, **kwargs) if key_func else 'default'
            if limiter.is_allowed(key):
                return func(*args, **kwargs)
            raise Exception("请求过于频繁")
        return wrapper
    return decorator

def main():
    limiter = DistributedRateLimiter(
        algorithm='sliding_window',
        max_requests=5,
        window_size=10
    )
    
    user_id = "user_123"
    for i in range(7):
        if limiter.is_allowed(user_id):
            print(f"请求 {i+1}: 允许")
        else:
            print(f"请求 {i+1}: 拒绝")


if __name__ == "__main__":
    main()
