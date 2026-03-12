# -----------------------------
# 题目：实现熔断器模式。
# 描述：防止级联故障，支持状态转换和恢复。
# -----------------------------

import time
from enum import Enum
from typing import Callable, Optional, Any
from threading import Lock

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        half_open_max_calls: int = 3
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.half_open_calls = 0
        self._lock = Lock()
    
    def call(self, func: Callable[[], Any], fallback: Callable[[], Any] = None) -> Any:
        with self._lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    self.half_open_calls = 0
                else:
                    if fallback:
                        return fallback()
                    raise Exception("熔断器处于开启状态")
        
        try:
            result = func()
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            if fallback:
                return fallback()
            raise
    
    def _should_attempt_reset(self) -> bool:
        if self.last_failure_time is None:
            return False
        return time.time() - self.last_failure_time >= self.recovery_timeout
    
    def _on_success(self):
        with self._lock:
            self.failure_count = 0
            
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                self.half_open_calls += 1
                
                if self.success_count >= self.half_open_max_calls:
                    self.state = CircuitState.CLOSED
                    self.success_count = 0
    
    def _on_failure(self):
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
                self.success_count = 0
            elif self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
    
    def get_state(self) -> CircuitState:
        return self.state
    
    def reset(self):
        with self._lock:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.last_failure_time = None

class CircuitBreakerRegistry:
    def __init__(self):
        self.breakers: dict = {}
        self._lock = Lock()
    
    def get_or_create(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0
    ) -> CircuitBreaker:
        with self._lock:
            if name not in self.breakers:
                self.breakers[name] = CircuitBreaker(
                    failure_threshold=failure_threshold,
                    recovery_timeout=recovery_timeout
                )
            return self.breakers[name]
    
    def get_all_states(self) -> dict:
        return {name: cb.get_state().value for name, cb in self.breakers.items()}

class ExternalService:
    def __init__(self, name: str, fail_rate: float = 0.0):
        self.name = name
        self.fail_rate = fail_rate
        self.call_count = 0
    
    def call(self) -> str:
        import random
        self.call_count += 1
        if random.random() < self.fail_rate:
            raise Exception(f"{self.name} 服务调用失败")
        return f"{self.name} 响应成功"

def main():
    registry = CircuitBreakerRegistry()
    
    service = ExternalService("payment-service", fail_rate=0.3)
    breaker = registry.get_or_create("payment", failure_threshold=3, recovery_timeout=5.0)
    
    for i in range(10):
        try:
            result = breaker.call(
                lambda: service.call(),
                fallback=lambda: "降级响应"
            )
            print(f"调用 {i+1}: {result}, 状态: {breaker.get_state().value}")
        except Exception as e:
            print(f"调用 {i+1}: 异常 - {e}, 状态: {breaker.get_state().value}")
        
        time.sleep(0.5)
    
    print(f"\n所有熔断器状态: {registry.get_all_states()}")

if __name__ == "__main__":
    main()
