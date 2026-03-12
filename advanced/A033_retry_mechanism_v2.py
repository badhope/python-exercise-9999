# -----------------------------
# 题目：实现简单的重试机制。
# -----------------------------

import time
import random
from typing import Callable, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

class RetryResult(Enum):
    SUCCESS = "success"
    RETRY = "retry"
    ABORT = "abort"

@dataclass
class RetryConfig:
    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    retryable_exceptions: List[type] = None
    
    def __post_init__(self):
        if self.retryable_exceptions is None:
            self.retryable_exceptions = [Exception]

class RetryState:
    def __init__(self, config: RetryConfig):
        self.config = config
        self.attempt = 0
        self.last_exception: Optional[Exception] = None
        self.total_delay: float = 0
    
    def next_attempt(self):
        self.attempt += 1
    
    def should_retry(self, exception: Exception) -> bool:
        self.last_exception = exception
        
        if self.attempt >= self.config.max_attempts:
            return False
        
        return any(isinstance(exception, exc_type) for exc_type in self.config.retryable_exceptions)
    
    def get_delay(self) -> float:
        delay = self.config.initial_delay * (self.config.exponential_base ** (self.attempt - 1))
        delay = min(delay, self.config.max_delay)
        
        if self.config.jitter:
            delay = delay * (0.5 + random.random())
        
        return delay

def retry(config: RetryConfig = None):
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            state = RetryState(config)
            
            while True:
                try:
                    state.next_attempt()
                    return func(*args, **kwargs)
                except Exception as e:
                    if not state.should_retry(e):
                        raise
                    
                    delay = state.get_delay()
                    state.total_delay += delay
                    
                    print(f"重试 {state.attempt}/{config.max_attempts}: {e}, 等待 {delay:.2f}秒")
                    time.sleep(delay)
        
        wrapper.retry_config = config
        return wrapper
    
    return decorator

class Retrier:
    def __init__(self, config: RetryConfig = None):
        self.config = config or RetryConfig()
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        state = RetryState(self.config)
        
        while True:
            try:
                state.next_attempt()
                return func(*args, **kwargs)
            except Exception as e:
                if not state.should_retry(e):
                    raise
                
                delay = state.get_delay()
                state.total_delay += delay
                
                time.sleep(delay)
    
    def execute_with_callback(self, func: Callable, on_retry: Callable = None, *args, **kwargs) -> Any:
        state = RetryState(self.config)
        
        while True:
            try:
                state.next_attempt()
                return func(*args, **kwargs)
            except Exception as e:
                if not state.should_retry(e):
                    raise
                
                delay = state.get_delay()
                state.total_delay += delay
                
                if on_retry:
                    on_retry(state.attempt, e, delay)
                
                time.sleep(delay)

class CircuitBreaker:
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = self.CLOSED
        self.failures = 0
        self.last_failure_time: Optional[float] = None
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        if self.state == self.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = self.HALF_OPEN
            else:
                raise Exception("熔断器处于打开状态")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        self.failures = 0
        self.state = self.CLOSED
    
    def _on_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        
        if self.failures >= self.failure_threshold:
            self.state = self.OPEN

def main():
    print("=== 重试装饰器测试 ===")
    
    call_count = 0
    
    @retry(RetryConfig(max_attempts=3, initial_delay=0.5))
    def unstable_function():
        nonlocal call_count
        call_count += 1
        
        if call_count < 3:
            raise ConnectionError("连接失败")
        
        return "成功"
    
    result = unstable_function()
    print(f"结果: {result}, 调用次数: {call_count}")
    
    print("\n=== Retrier类测试 ===")
    
    def another_unstable():
        global another_count
        another_count = getattr(globals(), 'another_count', 0) + 1
        
        if another_count < 2:
            raise TimeoutError("超时")
        
        return "完成"
    
    retrier = Retrier(RetryConfig(max_attempts=3, retryable_exceptions=[TimeoutError]))
    result = retrier.execute(another_unstable)
    print(f"结果: {result}")
    
    print("\n=== 熔断器测试 ===")
    
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=1)
    
    def failing_service():
        raise Exception("服务不可用")
    
    for i in range(5):
        try:
            cb.execute(failing_service)
        except Exception as e:
            print(f"调用 {i+1}: {e} (状态: {cb.state})")
    
    print(f"\n等待恢复...")
    time.sleep(1.5)
    
    print(f"当前状态: {cb.state}")


if __name__ == "__main__":
    main()
