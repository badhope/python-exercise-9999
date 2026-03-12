# -----------------------------
# 题目：实现熔断降级框架。
# 描述：支持熔断状态机、降级策略、自动恢复。
# -----------------------------

import time
import threading
from abc import ABC, abstractmethod
from typing import Callable, Any, Optional, Dict, List
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps

class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

@dataclass
class CircuitStats:
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    
    @property
    def failure_rate(self) -> float:
        if self.total_calls == 0:
            return 0.0
        return self.failed_calls / self.total_calls
    
    @property
    def success_rate(self) -> float:
        if self.total_calls == 0:
            return 0.0
        return self.successful_calls / self.total_calls

@dataclass
class CircuitConfig:
    failure_threshold: int = 5
    failure_rate_threshold: float = 0.5
    success_threshold: int = 3
    timeout: float = 30.0
    sliding_window_size: int = 100

class FallbackStrategy(ABC):
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        pass

class DefaultValueFallback(FallbackStrategy):
    def __init__(self, default_value: Any):
        self.default_value = default_value
    
    def execute(self, *args, **kwargs) -> Any:
        return self.default_value

class CacheFallback(FallbackStrategy):
    def __init__(self, cache: Dict[str, Any], key_func: Callable = None):
        self.cache = cache
        self.key_func = key_func or (lambda *a, **k: str(a))
    
    def execute(self, *args, **kwargs) -> Any:
        key = self.key_func(*args, **kwargs)
        return self.cache.get(key)

class CircuitBreaker:
    def __init__(
        self,
        name: str,
        config: CircuitConfig = None,
        fallback: FallbackStrategy = None
    ):
        self.name = name
        self.config = config or CircuitConfig()
        self.fallback = fallback
        self.state = CircuitState.CLOSED
        self.stats = CircuitStats()
        self._call_history: List[bool] = []
        self._lock = threading.RLock()
        self._half_open_successes = 0
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        with self._lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    self._half_open_successes = 0
                else:
                    return self._execute_fallback(*args, **kwargs)
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            return self._execute_fallback(*args, **kwargs)
    
    def _should_attempt_reset(self) -> bool:
        if self.stats.last_failure_time is None:
            return False
        return time.time() - self.stats.last_failure_time >= self.config.timeout
    
    def _on_success(self):
        with self._lock:
            self.stats.successful_calls += 1
            self.stats.total_calls += 1
            self.stats.last_success_time = time.time()
            
            self._record_call(True)
            
            if self.state == CircuitState.HALF_OPEN:
                self._half_open_successes += 1
                if self._half_open_successes >= self.config.success_threshold:
                    self.state = CircuitState.CLOSED
                    self._reset_stats()
    
    def _on_failure(self):
        with self._lock:
            self.stats.failed_calls += 1
            self.stats.total_calls += 1
            self.stats.last_failure_time = time.time()
            
            self._record_call(False)
            
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
            elif self.state == CircuitState.CLOSED:
                if self._should_open():
                    self.state = CircuitState.OPEN
    
    def _record_call(self, success: bool):
        self._call_history.append(success)
        if len(self._call_history) > self.config.sliding_window_size:
            self._call_history.pop(0)
    
    def _should_open(self) -> bool:
        if self.stats.failed_calls >= self.config.failure_threshold:
            return True
        
        if len(self._call_history) >= self.config.sliding_window_size:
            failure_rate = 1 - sum(self._call_history) / len(self._call_history)
            if failure_rate >= self.config.failure_rate_threshold:
                return True
        
        return False
    
    def _execute_fallback(self, *args, **kwargs) -> Any:
        if self.fallback:
            return self.fallback.execute(*args, **kwargs)
        raise Exception(f"熔断器 {self.name} 处于开启状态")
    
    def _reset_stats(self):
        self.stats = CircuitStats()
        self._call_history.clear()
    
    def force_open(self):
        with self._lock:
            self.state = CircuitState.OPEN
            self.stats.last_failure_time = time.time()
    
    def force_close(self):
        with self._lock:
            self.state = CircuitState.CLOSED
            self._reset_stats()
    
    def get_state(self) -> CircuitState:
        return self.state
    
    def get_metrics(self) -> Dict[str, Any]:
        with self._lock:
            return {
                'name': self.name,
                'state': self.state.value,
                'total_calls': self.stats.total_calls,
                'successful_calls': self.stats.successful_calls,
                'failed_calls': self.stats.failed_calls,
                'failure_rate': f"{self.stats.failure_rate:.2%}",
                'last_failure_time': self.stats.last_failure_time
            }

class CircuitBreakerRegistry:
    def __init__(self):
        self._breakers: Dict[str, CircuitBreaker] = {}
        self._lock = threading.Lock()
    
    def create(
        self,
        name: str,
        config: CircuitConfig = None,
        fallback: FallbackStrategy = None
    ) -> CircuitBreaker:
        breaker = CircuitBreaker(name, config, fallback)
        with self._lock:
            self._breakers[name] = breaker
        return breaker
    
    def get(self, name: str) -> Optional[CircuitBreaker]:
        return self._breakers.get(name)
    
    def get_all_metrics(self) -> List[Dict[str, Any]]:
        return [breaker.get_metrics() for breaker in self._breakers.values()]

def circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    timeout: float = 30.0,
    fallback: Callable = None
):
    registry = CircuitBreakerRegistry()
    
    fb = None
    if fallback:
        fb = DefaultValueFallback(None)
    
    breaker = registry.create(
        name,
        CircuitConfig(failure_threshold=failure_threshold, timeout=timeout),
        fb
    )
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return breaker.call(func, *args, **kwargs)
        return wrapper
    
    return decorator

def main():
    registry = CircuitBreakerRegistry()
    
    fallback = DefaultValueFallback({"status": "degraded", "data": None})
    
    breaker = registry.create(
        "external-api",
        CircuitConfig(
            failure_threshold=3,
            success_threshold=2,
            timeout=2.0
        ),
        fallback
    )
    
    def unreliable_service():
        import random
        if random.random() < 0.6:
            raise Exception("服务不可用")
        return {"status": "ok", "data": "success"}
    
    print("模拟服务调用:")
    for i in range(15):
        result = breaker.call(unreliable_service)
        state = breaker.get_state().value
        print(f"调用 {i+1}: 状态={state}, 结果={result}")
        
        time.sleep(0.3)
    
    print(f"\n熔断器指标: {breaker.get_metrics()}")

if __name__ == "__main__":
    main()
