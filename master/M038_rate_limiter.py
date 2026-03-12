# -----------------------------
# 题目：实现限流器。
# 描述：支持令牌桶、漏桶、滑动窗口算法。
# -----------------------------

import time
import threading
from abc import ABC, abstractmethod
from typing import Dict, Optional
from collections import deque

class RateLimiter(ABC):
    @abstractmethod
    def acquire(self, permits: int = 1) -> bool:
        pass
    
    @abstractmethod
    def get_available_permits(self) -> int:
        pass

class TokenBucketRateLimiter(RateLimiter):
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill_time = time.time()
        self._lock = threading.Lock()
    
    def acquire(self, permits: int = 1) -> bool:
        with self._lock:
            self._refill()
            
            if self.tokens >= permits:
                self.tokens -= permits
                return True
            return False
    
    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill_time
        
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill_time = now
    
    def get_available_permits(self) -> int:
        with self._lock:
            self._refill()
            return int(self.tokens)
    
    def try_acquire(self, permits: int = 1, timeout: float = 0) -> bool:
        start_time = time.time()
        
        while True:
            if self.acquire(permits):
                return True
            
            if time.time() - start_time >= timeout:
                return False
            
            time.sleep(0.01)

class LeakyBucketRateLimiter(RateLimiter):
    def __init__(self, capacity: int, leak_rate: float):
        self.capacity = capacity
        self.leak_rate = leak_rate
        self.water = 0
        self.last_leak_time = time.time()
        self._lock = threading.Lock()
    
    def acquire(self, permits: int = 1) -> bool:
        with self._lock:
            self._leak()
            
            if self.water + permits <= self.capacity:
                self.water += permits
                return True
            return False
    
    def _leak(self):
        now = time.time()
        elapsed = now - self.last_leak_time
        
        leaked = elapsed * self.leak_rate
        self.water = max(0, self.water - leaked)
        self.last_leak_time = now
    
    def get_available_permits(self) -> int:
        with self._lock:
            self._leak()
            return int(self.capacity - self.water)

class SlidingWindowRateLimiter(RateLimiter):
    def __init__(self, window_size: int, max_requests: int):
        self.window_size = window_size
        self.max_requests = max_requests
        self.requests = deque()
        self._lock = threading.Lock()
    
    def acquire(self, permits: int = 1) -> bool:
        with self._lock:
            now = time.time()
            
            cutoff = now - self.window_size
            while self.requests and self.requests[0] < cutoff:
                self.requests.popleft()
            
            if len(self.requests) + permits <= self.max_requests:
                for _ in range(permits):
                    self.requests.append(now)
                return True
            return False
    
    def get_available_permits(self) -> int:
        with self._lock:
            now = time.time()
            cutoff = now - self.window_size
            while self.requests and self.requests[0] < cutoff:
                self.requests.popleft()
            return max(0, self.max_requests - len(self.requests))

class FixedWindowRateLimiter(RateLimiter):
    def __init__(self, window_size: float, max_requests: int):
        self.window_size = window_size
        self.max_requests = max_requests
        self.window_start = time.time()
        self.request_count = 0
        self._lock = threading.Lock()
    
    def acquire(self, permits: int = 1) -> bool:
        with self._lock:
            now = time.time()
            
            if now - self.window_start >= self.window_size:
                self.window_start = now
                self.request_count = 0
            
            if self.request_count + permits <= self.max_requests:
                self.request_count += permits
                return True
            return False
    
    def get_available_permits(self) -> int:
        with self._lock:
            now = time.time()
            if now - self.window_start >= self.window_size:
                return self.max_requests
            return max(0, self.max_requests - self.request_count)

class RateLimiterRegistry:
    def __init__(self):
        self._limiters: Dict[str, RateLimiter] = {}
        self._lock = threading.Lock()
    
    def create_token_bucket(self, name: str, capacity: int, refill_rate: float) -> TokenBucketRateLimiter:
        limiter = TokenBucketRateLimiter(capacity, refill_rate)
        with self._lock:
            self._limiters[name] = limiter
        return limiter
    
    def create_sliding_window(self, name: str, window_size: int, max_requests: int) -> SlidingWindowRateLimiter:
        limiter = SlidingWindowRateLimiter(window_size, max_requests)
        with self._lock:
            self._limiters[name] = limiter
        return limiter
    
    def get(self, name: str) -> Optional[RateLimiter]:
        with self._lock:
            return self._limiters.get(name)
    
    def acquire(self, name: str, permits: int = 1) -> bool:
        limiter = self.get(name)
        if limiter:
            return limiter.acquire(permits)
        return False

def rate_limit(limiter: RateLimiter, permits: int = 1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not limiter.acquire(permits):
                raise Exception("请求被限流")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def main():
    print("=== 令牌桶限流器 ===")
    token_bucket = TokenBucketRateLimiter(capacity=10, refill_rate=2)
    
    for i in range(15):
        result = token_bucket.acquire()
        available = token_bucket.get_available_permits()
        print(f"请求 {i+1}: {'通过' if result else '被限流'}, 剩余令牌: {available}")
    
    print("\n=== 滑动窗口限流器 ===")
    sliding_window = SlidingWindowRateLimiter(window_size=1, max_requests=5)
    
    for i in range(10):
        result = sliding_window.acquire()
        available = sliding_window.get_available_permits()
        print(f"请求 {i+1}: {'通过' if result else '被限流'}, 可用配额: {available}")
    
    print("\n=== 限流器注册表 ===")
    registry = RateLimiterRegistry()
    registry.create_token_bucket("api", capacity=100, refill_rate=10)
    registry.create_sliding_window("login", window_size=60, max_requests=5)
    
    print(f"API限流器: {registry.acquire('api')}")
    print(f"登录限流器: {registry.acquire('login')}")

if __name__ == "__main__":
    main()
