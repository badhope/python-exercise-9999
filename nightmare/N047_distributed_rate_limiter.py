"""
N047 - 分布式限流系统
难度：Nightmare

题目描述：
实现一个分布式限流系统，支持多种限流算法（令牌桶、漏桶、滑动窗口、固定窗口）。
系统需要处理分布式环境下的限流协调、限流规则动态配置和限流统计。

学习目标：
1. 理解各种限流算法的原理和适用场景
2. 掌握分布式限流的实现方法
3. 实现限流规则的动态配置
4. 处理限流统计和监控

输入输出要求：
输入：限流请求（资源标识、请求信息）
输出：限流结果（允许/拒绝、剩余配额）

预期解决方案：
使用不同的限流算法实现，通过分布式协调保证限流的一致性。
"""

import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


class RateLimitAlgorithm(Enum):
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"


@dataclass
class RateLimitRule:
    resource: str
    algorithm: RateLimitAlgorithm
    capacity: int
    refill_rate: float
    window_size: float = 1.0
    enabled: bool = True


@dataclass
class RateLimitResult:
    allowed: bool
    remaining: int
    reset_at: float
    retry_after: Optional[float] = None


@dataclass
class RateLimitStats:
    resource: str
    total_requests: int = 0
    allowed_requests: int = 0
    rejected_requests: int = 0
    last_request_time: float = 0


class RateLimiterBase(ABC):
    @abstractmethod
    def try_acquire(self, key: str, tokens: int = 1) -> RateLimitResult:
        pass
    
    @abstractmethod
    def get_stats(self, key: str) -> Optional[RateLimitStats]:
        pass


class TokenBucketLimiter(RateLimiterBase):
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self._buckets: Dict[str, Dict] = {}
        self._stats: Dict[str, RateLimitStats] = {}
        self._lock = threading.Lock()
    
    def try_acquire(self, key: str, tokens: int = 1) -> RateLimitResult:
        with self._lock:
            now = time.time()
            
            if key not in self._buckets:
                self._buckets[key] = {
                    "tokens": self.capacity,
                    "last_refill": now
                }
                self._stats[key] = RateLimitStats(resource=key)
            
            bucket = self._buckets[key]
            stats = self._stats[key]
            
            elapsed = now - bucket["last_refill"]
            refill = elapsed * self.refill_rate
            bucket["tokens"] = min(self.capacity, bucket["tokens"] + refill)
            bucket["last_refill"] = now
            
            stats.total_requests += 1
            stats.last_request_time = now
            
            if bucket["tokens"] >= tokens:
                bucket["tokens"] -= tokens
                stats.allowed_requests += 1
                
                return RateLimitResult(
                    allowed=True,
                    remaining=int(bucket["tokens"]),
                    reset_at=now + (self.capacity - bucket["tokens"]) / self.refill_rate
                )
            else:
                stats.rejected_requests += 1
                retry_after = (tokens - bucket["tokens"]) / self.refill_rate
                
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_at=now + retry_after,
                    retry_after=retry_after
                )
    
    def get_stats(self, key: str) -> Optional[RateLimitStats]:
        with self._lock:
            return self._stats.get(key)


class LeakyBucketLimiter(RateLimiterBase):
    def __init__(self, capacity: int, leak_rate: float):
        self.capacity = capacity
        self.leak_rate = leak_rate
        self._buckets: Dict[str, Dict] = {}
        self._stats: Dict[str, RateLimitStats] = {}
        self._lock = threading.Lock()
    
    def try_acquire(self, key: str, tokens: int = 1) -> RateLimitResult:
        with self._lock:
            now = time.time()
            
            if key not in self._buckets:
                self._buckets[key] = {
                    "water": 0,
                    "last_leak": now
                }
                self._stats[key] = RateLimitStats(resource=key)
            
            bucket = self._buckets[key]
            stats = self._stats[key]
            
            elapsed = now - bucket["last_leak"]
            leak = elapsed * self.leak_rate
            bucket["water"] = max(0, bucket["water"] - leak)
            bucket["last_leak"] = now
            
            stats.total_requests += 1
            stats.last_request_time = now
            
            if bucket["water"] + tokens <= self.capacity:
                bucket["water"] += tokens
                stats.allowed_requests += 1
                
                return RateLimitResult(
                    allowed=True,
                    remaining=self.capacity - int(bucket["water"]),
                    reset_at=now + bucket["water"] / self.leak_rate
                )
            else:
                stats.rejected_requests += 1
                retry_after = (bucket["water"] + tokens - self.capacity) / self.leak_rate
                
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_at=now + retry_after,
                    retry_after=retry_after
                )
    
    def get_stats(self, key: str) -> Optional[RateLimitStats]:
        with self._lock:
            return self._stats.get(key)


class SlidingWindowLimiter(RateLimiterBase):
    def __init__(self, capacity: int, window_size: float):
        self.capacity = capacity
        self.window_size = window_size
        self._windows: Dict[str, List[float]] = {}
        self._stats: Dict[str, RateLimitStats] = {}
        self._lock = threading.Lock()
    
    def try_acquire(self, key: str, tokens: int = 1) -> RateLimitResult:
        with self._lock:
            now = time.time()
            
            if key not in self._windows:
                self._windows[key] = []
                self._stats[key] = RateLimitStats(resource=key)
            
            window = self._windows[key]
            stats = self._stats[key]
            
            cutoff = now - self.window_size
            while window and window[0] < cutoff:
                window.pop(0)
            
            stats.total_requests += 1
            stats.last_request_time = now
            
            current_count = len(window)
            
            if current_count + tokens <= self.capacity:
                for _ in range(tokens):
                    window.append(now)
                stats.allowed_requests += 1
                
                return RateLimitResult(
                    allowed=True,
                    remaining=self.capacity - len(window),
                    reset_at=now + self.window_size
                )
            else:
                stats.rejected_requests += 1
                retry_after = window[0] + self.window_size - now if window else self.window_size
                
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_at=now + retry_after,
                    retry_after=retry_after
                )
    
    def get_stats(self, key: str) -> Optional[RateLimitStats]:
        with self._lock:
            return self._stats.get(key)


class FixedWindowLimiter(RateLimiterBase):
    def __init__(self, capacity: int, window_size: float):
        self.capacity = capacity
        self.window_size = window_size
        self._windows: Dict[str, Dict] = {}
        self._stats: Dict[str, RateLimitStats] = {}
        self._lock = threading.Lock()
    
    def try_acquire(self, key: str, tokens: int = 1) -> RateLimitResult:
        with self._lock:
            now = time.time()
            window_start = (now // self.window_size) * self.window_size
            window_end = window_start + self.window_size
            
            if key not in self._windows:
                self._windows[key] = {
                    "count": 0,
                    "window_start": window_start
                }
                self._stats[key] = RateLimitStats(resource=key)
            
            window = self._windows[key]
            stats = self._stats[key]
            
            if window["window_start"] != window_start:
                window["count"] = 0
                window["window_start"] = window_start
            
            stats.total_requests += 1
            stats.last_request_time = now
            
            if window["count"] + tokens <= self.capacity:
                window["count"] += tokens
                stats.allowed_requests += 1
                
                return RateLimitResult(
                    allowed=True,
                    remaining=self.capacity - window["count"],
                    reset_at=window_end
                )
            else:
                stats.rejected_requests += 1
                
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_at=window_end,
                    retry_after=window_end - now
                )
    
    def get_stats(self, key: str) -> Optional[RateLimitStats]:
        with self._lock:
            return self._stats.get(key)


class DistributedRateLimiter:
    def __init__(self):
        self._rules: Dict[str, RateLimitRule] = {}
        self._limiters: Dict[str, RateLimiterBase] = {}
        self._global_stats: Dict[str, RateLimitStats] = {}
        self._lock = threading.Lock()
    
    def add_rule(self, rule: RateLimitRule):
        with self._lock:
            self._rules[rule.resource] = rule
            
            if rule.algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
                limiter = TokenBucketLimiter(rule.capacity, rule.refill_rate)
            elif rule.algorithm == RateLimitAlgorithm.LEAKY_BUCKET:
                limiter = LeakyBucketLimiter(rule.capacity, rule.refill_rate)
            elif rule.algorithm == RateLimitAlgorithm.SLIDING_WINDOW:
                limiter = SlidingWindowLimiter(rule.capacity, rule.window_size)
            else:
                limiter = FixedWindowLimiter(rule.capacity, rule.window_size)
            
            self._limiters[rule.resource] = limiter
    
    def remove_rule(self, resource: str) -> bool:
        with self._lock:
            if resource in self._rules:
                del self._rules[resource]
                del self._limiters[resource]
                return True
        return False
    
    def update_rule(self, resource: str, **kwargs) -> bool:
        with self._lock:
            if resource not in self._rules:
                return False
            
            rule = self._rules[resource]
            
            if "capacity" in kwargs:
                rule.capacity = kwargs["capacity"]
            if "refill_rate" in kwargs:
                rule.refill_rate = kwargs["refill_rate"]
            if "enabled" in kwargs:
                rule.enabled = kwargs["enabled"]
            
            self.add_rule(rule)
            return True
    
    def check_rate_limit(self, resource: str, key: str, tokens: int = 1) -> RateLimitResult:
        with self._lock:
            rule = self._rules.get(resource)
            if not rule or not rule.enabled:
                return RateLimitResult(
                    allowed=True,
                    remaining=-1,
                    reset_at=time.time()
                )
            
            limiter = self._limiters.get(resource)
            if not limiter:
                return RateLimitResult(
                    allowed=True,
                    remaining=-1,
                    reset_at=time.time()
                )
        
        return limiter.try_acquire(key, tokens)
    
    def get_resource_stats(self, resource: str) -> Dict[str, RateLimitStats]:
        with self._lock:
            limiter = self._limiters.get(resource)
            if not limiter:
                return {}
            
            if hasattr(limiter, "_stats"):
                return dict(limiter._stats)
        return {}
    
    def get_all_stats(self) -> Dict[str, Dict[str, RateLimitStats]]:
        result = {}
        with self._lock:
            for resource in self._rules:
                result[resource] = self.get_resource_stats(resource)
        return result
    
    def get_rule(self, resource: str) -> Optional[RateLimitRule]:
        with self._lock:
            return self._rules.get(resource)
    
    def list_rules(self) -> List[RateLimitRule]:
        with self._lock:
            return list(self._rules.values())


class RateLimitMiddleware:
    def __init__(self, rate_limiter: DistributedRateLimiter):
        self.rate_limiter = rate_limiter
        self._request_hooks: List = []
        self._response_hooks: List = []
    
    def add_request_hook(self, hook):
        self._request_hooks.append(hook)
    
    def add_response_hook(self, hook):
        self._response_hooks.append(hook)
    
    def process_request(self, resource: str, client_id: str, 
                        request_data: dict = None) -> Tuple[bool, RateLimitResult]:
        for hook in self._request_hooks:
            hook(resource, client_id, request_data)
        
        result = self.rate_limiter.check_rate_limit(resource, client_id)
        
        for hook in self._response_hooks:
            hook(resource, client_id, result)
        
        return result.allowed, result
    
    def get_client_remaining(self, resource: str, client_id: str) -> int:
        result = self.rate_limiter.check_rate_limit(resource, client_id, 0)
        return result.remaining


def main():
    rate_limiter = DistributedRateLimiter()
    
    print("=== 添加限流规则 ===")
    rate_limiter.add_rule(RateLimitRule(
        resource="api",
        algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
        capacity=10,
        refill_rate=2
    ))
    
    rate_limiter.add_rule(RateLimitRule(
        resource="login",
        algorithm=RateLimitAlgorithm.SLIDING_WINDOW,
        capacity=5,
        refill_rate=1,
        window_size=60
    ))
    
    rate_limiter.add_rule(RateLimitRule(
        resource="download",
        algorithm=RateLimitAlgorithm.LEAKY_BUCKET,
        capacity=20,
        refill_rate=5
    ))
    
    rate_limiter.add_rule(RateLimitRule(
        resource="search",
        algorithm=RateLimitAlgorithm.FIXED_WINDOW,
        capacity=100,
        refill_rate=1,
        window_size=60
    ))
    
    print("\n=== 测试令牌桶限流 ===")
    for i in range(15):
        result = rate_limiter.check_rate_limit("api", "user1")
        status = "✓" if result.allowed else "✗"
        print(f"请求 {i+1}: {status} (剩余: {result.remaining})")
        if not result.allowed:
            print(f"  需等待 {result.retry_after:.2f} 秒")
            break
    
    print("\n=== 测试滑动窗口限流 ===")
    for i in range(8):
        result = rate_limiter.check_rate_limit("login", "user2")
        status = "✓" if result.allowed else "✗"
        print(f"请求 {i+1}: {status} (剩余: {result.remaining})")
    
    print("\n=== 测试漏桶限流 ===")
    for i in range(25):
        result = rate_limiter.check_rate_limit("download", "user3")
        if i % 5 == 0:
            status = "✓" if result.allowed else "✗"
            print(f"请求 {i+1}: {status} (剩余: {result.remaining})")
    
    print("\n=== 测试固定窗口限流 ===")
    for i in range(105):
        result = rate_limiter.check_rate_limit("search", "user4")
        if i >= 98:
            status = "✓" if result.allowed else "✗"
            print(f"请求 {i+1}: {status} (剩余: {result.remaining})")
    
    print("\n=== 动态更新规则 ===")
    rate_limiter.update_rule("api", capacity=20)
    rule = rate_limiter.get_rule("api")
    print(f"API限流容量更新为: {rule.capacity}")
    
    print("\n=== 查看限流统计 ===")
    api_stats = rate_limiter.get_resource_stats("api")
    for key, stats in list(api_stats.items())[:3]:
        print(f"客户端 {key}:")
        print(f"  总请求: {stats.total_requests}")
        print(f"  允许: {stats.allowed_requests}")
        print(f"  拒绝: {stats.rejected_requests}")
    
    print("\n=== 使用中间件 ===")
    middleware = RateLimitMiddleware(rate_limiter)
    
    def log_request(resource, client_id, data):
        print(f"[请求] 资源: {resource}, 客户端: {client_id}")
    
    def log_response(resource, client_id, result):
        if not result.allowed:
            print(f"[拒绝] 客户端 {client_id} 被限流")
    
    middleware.add_request_hook(log_request)
    middleware.add_response_hook(log_response)
    
    for i in range(3):
        allowed, result = middleware.process_request("api", "user5")
        print(f"中间件处理结果: {'通过' if allowed else '拒绝'}")


if __name__ == "__main__":
    main()
