# -----------------------------
# 题目：实现限流器。
# -----------------------------

import time
import threading
from collections import deque

class RateLimiter:
    def __init__(self, max_requests, time_window):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()
        self.lock = threading.Lock()
    
    def allow(self):
        with self.lock:
            now = time.time()
            
            while self.requests and self.requests[0] < now - self.time_window:
                self.requests.popleft()
            
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True
            return False
    
    def wait_and_allow(self):
        while True:
            if self.allow():
                return True
            time.sleep(0.01)

class TokenBucket:
    def __init__(self, capacity, refill_rate):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
        self.lock = threading.Lock()
    
    def allow(self, tokens=1):
        with self.lock:
            self._refill()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

if __name__ == "__main__":
    limiter = RateLimiter(5, 1)
    
    for i in range(10):
        result = limiter.allow()
        print(f"Request {i+1}: {'Allowed' if result else 'Rejected'}")
        time.sleep(0.2)
