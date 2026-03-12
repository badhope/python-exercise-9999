# -----------------------------
# 题目：实现分布式限流器。
# 描述：支持滑动窗口、令牌桶、分布式计数。
# -----------------------------

import time
import threading
import hashlib
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict, deque
from bisect import bisect_left

@dataclass
class RateLimitConfig:
    max_requests: int
    window_size: float
    key_func: callable = None

class SlidingWindowCounter:
    def __init__(self, window_size: float, max_requests: int):
        self.window_size = window_size
        self.max_requests = max_requests
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self._lock = threading.Lock()
    
    def is_allowed(self, key: str) -> bool:
        with self._lock:
            now = time.time()
            cutoff = now - self.window_size
            
            requests = self.requests[key]
            
            while requests and requests[0] < cutoff:
                requests.pop(0)
            
            if len(requests) < self.max_requests:
                requests.append(now)
                return True
            
            return False
    
    def get_count(self, key: str) -> int:
        with self._lock:
            now = time.time()
            cutoff = now - self.window_size
            
            requests = self.requests[key]
            while requests and requests[0] < cutoff:
                requests.pop(0)
            
            return len(requests)

class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.buckets: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
    
    def is_allowed(self, key: str, tokens: int = 1) -> bool:
        with self._lock:
            now = time.time()
            
            if key not in self.buckets:
                self.buckets[key] = {
                    'tokens': self.capacity,
                    'last_refill': now
                }
            
            bucket = self.buckets[key]
            elapsed = now - bucket['last_refill']
            
            bucket['tokens'] = min(
                self.capacity,
                bucket['tokens'] + elapsed * self.refill_rate
            )
            bucket['last_refill'] = now
            
            if bucket['tokens'] >= tokens:
                bucket['tokens'] -= tokens
                return True
            
            return False
    
    def get_tokens(self, key: str) -> float:
        with self._lock:
            if key not in self.buckets:
                return self.capacity
            
            now = time.time()
            bucket = self.buckets[key]
            elapsed = now - bucket['last_refill']
            
            return min(
                self.capacity,
                bucket['tokens'] + elapsed * self.refill_rate
            )

class LeakyBucket:
    def __init__(self, capacity: int, leak_rate: float):
        self.capacity = capacity
        self.leak_rate = leak_rate
        self.buckets: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
    
    def is_allowed(self, key: str) -> bool:
        with self._lock:
            now = time.time()
            
            if key not in self.buckets:
                self.buckets[key] = {
                    'water': 0,
                    'last_leak': now
                }
            
            bucket = self.buckets[key]
            elapsed = now - bucket['last_leak']
            
            bucket['water'] = max(0, bucket['water'] - elapsed * self.leak_rate)
            bucket['last_leak'] = now
            
            if bucket['water'] < self.capacity:
                bucket['water'] += 1
                return True
            
            return False

class DistributedRateLimiter:
    def __init__(self):
        self.sliding_windows: Dict[str, SlidingWindowCounter] = {}
        self.token_buckets: Dict[str, TokenBucket] = {}
        self.leaky_buckets: Dict[str, LeakyBucket] = {}
        self._lock = threading.Lock()
    
    def create_sliding_window(
        self,
        name: str,
        window_size: float,
        max_requests: int
    ):
        with self._lock:
            self.sliding_windows[name] = SlidingWindowCounter(window_size, max_requests)
    
    def create_token_bucket(
        self,
        name: str,
        capacity: int,
        refill_rate: float
    ):
        with self._lock:
            self.token_buckets[name] = TokenBucket(capacity, refill_rate)
    
    def create_leaky_bucket(
        self,
        name: str,
        capacity: int,
        leak_rate: float
    ):
        with self._lock:
            self.leaky_buckets[name] = LeakyBucket(capacity, leak_rate)
    
    def check_sliding_window(self, name: str, key: str) -> bool:
        limiter = self.sliding_windows.get(name)
        if limiter:
            return limiter.is_allowed(key)
        return True
    
    def check_token_bucket(self, name: str, key: str, tokens: int = 1) -> bool:
        limiter = self.token_buckets.get(name)
        if limiter:
            return limiter.is_allowed(key, tokens)
        return True
    
    def check_leaky_bucket(self, name: str, key: str) -> bool:
        limiter = self.leaky_buckets.get(name)
        if limiter:
            return limiter.is_allowed(key)
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'sliding_windows': list(self.sliding_windows.keys()),
            'token_buckets': list(self.token_buckets.keys()),
            'leaky_buckets': list(self.leaky_buckets.keys())
        }

class RateLimitMiddleware:
    def __init__(self, limiter: DistributedRateLimiter):
        self.limiter = limiter
        self.rules: Dict[str, Dict[str, Any]] = {}
    
    def add_rule(
        self,
        path_pattern: str,
        limit_type: str,
        limit_name: str,
        key_extractor: callable = None
    ):
        self.rules[path_pattern] = {
            'limit_type': limit_type,
            'limit_name': limit_name,
            'key_extractor': key_extractor or (lambda req: req.get('ip', 'default'))
        }
    
    def check(self, request: Dict[str, Any]) -> bool:
        path = request.get('path', '')
        
        for pattern, rule in self.rules.items():
            if self._match_pattern(pattern, path):
                key = rule['key_extractor'](request)
                
                if rule['limit_type'] == 'sliding_window':
                    return self.limiter.check_sliding_window(rule['limit_name'], key)
                elif rule['limit_type'] == 'token_bucket':
                    return self.limiter.check_token_bucket(rule['limit_name'], key)
                elif rule['limit_type'] == 'leaky_bucket':
                    return self.limiter.check_leaky_bucket(rule['limit_name'], key)
        
        return True
    
    def _match_pattern(self, pattern: str, path: str) -> bool:
        return pattern in path or pattern == '*'

def main():
    limiter = DistributedRateLimiter()
    
    limiter.create_sliding_window("api", window_size=1.0, max_requests=5)
    limiter.create_token_bucket("download", capacity=10, refill_rate=1.0)
    limiter.create_leaky_bucket("upload", capacity=5, leak_rate=0.5)
    
    print("=== 滑动窗口限流 ===")
    for i in range(10):
        result = limiter.check_sliding_window("api", "user-1")
        print(f"请求 {i+1}: {'通过' if result else '被限流'}")
    
    print("\n=== 令牌桶限流 ===")
    for i in range(15):
        result = limiter.check_token_bucket("download", "user-1")
        tokens = limiter.token_buckets["download"].get_tokens("user-1")
        print(f"请求 {i+1}: {'通过' if result else '被限流'}, 剩余令牌: {tokens:.1f}")
    
    print("\n=== 中间件限流 ===")
    middleware = RateLimitMiddleware(limiter)
    middleware.add_rule("/api/*", "sliding_window", "api", lambda r: r.get('user_id', 'default'))
    
    for i in range(8):
        request = {'path': '/api/users', 'user_id': 'user-1'}
        result = middleware.check(request)
        print(f"API请求 {i+1}: {'通过' if result else '被限流'}")

if __name__ == "__main__":
    main()
