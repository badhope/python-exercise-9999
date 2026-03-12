# -----------------------------
# 题目：实现重试模式。
# 描述：支持指数退避、抖动、最大重试次数。
# -----------------------------

import time
import random
from typing import Callable, Optional, List, Type, Any
from dataclasses import dataclass
from functools import wraps

@dataclass
class RetryConfig:
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    retryable_exceptions: List[Type[Exception]] = None
    
    def __post_init__(self):
        if self.retryable_exceptions is None:
            self.retryable_exceptions = [Exception]

class RetryResult:
    def __init__(self, success: bool, result: Any = None, exception: Exception = None, attempts: int = 0):
        self.success = success
        self.result = result
        self.exception = exception
        self.attempts = attempts

class RetryPolicy:
    def __init__(self, config: RetryConfig = None):
        self.config = config or RetryConfig()
    
    def execute(self, func: Callable[[], Any]) -> RetryResult:
        last_exception = None
        
        for attempt in range(1, self.config.max_attempts + 1):
            try:
                result = func()
                return RetryResult(success=True, result=result, attempts=attempt)
            except Exception as e:
                last_exception = e
                
                if not self._is_retryable(e):
                    return RetryResult(success=False, exception=e, attempts=attempt)
                
                if attempt < self.config.max_attempts:
                    delay = self._calculate_delay(attempt)
                    time.sleep(delay)
        
        return RetryResult(
            success=False,
            exception=last_exception,
            attempts=self.config.max_attempts
        )
    
    def _is_retryable(self, exception: Exception) -> bool:
        return any(
            isinstance(exception, exc_type)
            for exc_type in self.config.retryable_exceptions
        )
    
    def _calculate_delay(self, attempt: int) -> float:
        delay = self.config.base_delay * (self.config.exponential_base ** (attempt - 1))
        delay = min(delay, self.config.max_delay)
        
        if self.config.jitter:
            delay = delay * (0.5 + random.random())
        
        return delay

def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: List[Type[Exception]] = None
):
    config = RetryConfig(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=max_delay,
        exponential_base=exponential_base,
        jitter=jitter,
        retryable_exceptions=retryable_exceptions
    )
    policy = RetryPolicy(config)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = policy.execute(lambda: func(*args, **kwargs))
            if result.success:
                return result.result
            raise result.exception
        return wrapper
    
    return decorator

class UnreliableService:
    def __init__(self, fail_until_attempt: int = 3):
        self.fail_until_attempt = fail_until_attempt
        self.call_count = 0
    
    def call(self) -> str:
        self.call_count += 1
        if self.call_count < self.fail_until_attempt:
            raise ConnectionError(f"连接失败 (尝试 {self.call_count})")
        return f"成功 (尝试 {self.call_count})"

class TimeoutError(Exception):
    pass

class NetworkError(Exception):
    pass

def main():
    service = UnreliableService(fail_until_attempt=3)
    
    config = RetryConfig(
        max_attempts=5,
        base_delay=0.5,
        max_delay=10.0,
        exponential_base=2.0,
        jitter=True,
        retryable_exceptions=[ConnectionError, TimeoutError, NetworkError]
    )
    policy = RetryPolicy(config)
    
    result = policy.execute(lambda: service.call())
    
    print(f"执行成功: {result.success}")
    print(f"结果: {result.result}")
    print(f"尝试次数: {result.attempts}")
    
    @retry(max_attempts=3, base_delay=0.1)
    def unreliable_function():
        import random
        if random.random() < 0.5:
            raise ValueError("随机失败")
        return "成功"
    
    try:
        result = unreliable_function()
        print(f"装饰器方式结果: {result}")
    except Exception as e:
        print(f"装饰器方式失败: {e}")

if __name__ == "__main__":
    main()
