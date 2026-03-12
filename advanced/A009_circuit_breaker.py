# -----------------------------
# 题目：实现简单的断路器模式。
# 描述：防止级联故障，支持熔断和恢复。
# -----------------------------

import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = None
    
    def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("断路器打开，拒绝请求")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
    
    def get_state(self):
        return self.state.value

def main():
    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=5)
    
    def risky_operation():
        import random
        if random.random() < 0.5:
            raise Exception("操作失败")
        return "成功"
    
    for i in range(10):
        try:
            result = breaker.call(risky_operation)
            print(f"调用 {i+1}: {result}")
        except Exception as e:
            print(f"调用 {i+1}: {e} (状态: {breaker.get_state()})")


if __name__ == "__main__":
    main()
