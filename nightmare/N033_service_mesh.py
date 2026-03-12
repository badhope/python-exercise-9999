# -----------------------------
# 题目：实现服务网格代理。
# 描述：支持服务发现、负载均衡、熔断限流。
# -----------------------------

import time
import threading
import random
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

class ServiceStatus(Enum):
    UP = "up"
    DOWN = "down"
    DEGRADED = "degraded"

@dataclass
class ServiceInstance:
    instance_id: str
    service_name: str
    host: str
    port: int
    weight: int = 1
    status: ServiceStatus = ServiceStatus.UP
    last_check: float = field(default_factory=time.time)

@dataclass
class CircuitBreakerState:
    failures: int = 0
    last_failure: float = 0
    state: str = "closed"
    half_open_calls: int = 0

class ServiceRegistry:
    def __init__(self):
        self.services: Dict[str, List[ServiceInstance]] = defaultdict(list)
        self._lock = threading.Lock()
    
    def register(self, instance: ServiceInstance):
        with self._lock:
            self.services[instance.service_name].append(instance)
    
    def deregister(self, service_name: str, instance_id: str):
        with self._lock:
            instances = self.services.get(service_name, [])
            self.services[service_name] = [
                i for i in instances if i.instance_id != instance_id
            ]
    
    def get_instances(self, service_name: str) -> List[ServiceInstance]:
        with self._lock:
            return [
                i for i in self.services.get(service_name, [])
                if i.status == ServiceStatus.UP
            ]

class LoadBalancer:
    def __init__(self):
        self._counters: Dict[str, int] = defaultdict(int)
    
    def select(self, instances: List[ServiceInstance], strategy: str = "round_robin") -> Optional[ServiceInstance]:
        if not instances:
            return None
        
        if strategy == "round_robin":
            service_name = instances[0].service_name
            idx = self._counters[service_name] % len(instances)
            self._counters[service_name] += 1
            return instances[idx]
        elif strategy == "random":
            return random.choice(instances)
        elif strategy == "weighted":
            total_weight = sum(i.weight for i in instances)
            r = random.uniform(0, total_weight)
            current = 0
            for inst in instances:
                current += inst.weight
                if current >= r:
                    return inst
            return instances[-1]
        
        return instances[0]

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 30.0,
        half_open_max_calls: int = 3
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.half_open_max_calls = half_open_max_calls
        self._states: Dict[str, CircuitBreakerState] = defaultdict(CircuitBreakerState)
        self._lock = threading.Lock()
    
    def is_allowed(self, key: str) -> bool:
        with self._lock:
            state = self._states[key]
            
            if state.state == "closed":
                return True
            
            if state.state == "open":
                if time.time() - state.last_failure >= self.timeout:
                    state.state = "half_open"
                    state.half_open_calls = 0
                    return True
                return False
            
            if state.state == "half_open":
                if state.half_open_calls < self.half_open_max_calls:
                    state.half_open_calls += 1
                    return True
                return False
            
            return True
    
    def record_success(self, key: str):
        with self._lock:
            state = self._states[key]
            state.failures = 0
            state.state = "closed"
    
    def record_failure(self, key: str):
        with self._lock:
            state = self._states[key]
            state.failures += 1
            state.last_failure = time.time()
            
            if state.state == "half_open":
                state.state = "open"
            elif state.failures >= self.failure_threshold:
                state.state = "open"

class RateLimiter:
    def __init__(self, requests_per_second: int = 100):
        self.requests_per_second = requests_per_second
        self._tokens: Dict[str, float] = defaultdict(lambda: float(requests_per_second))
        self._last_update: Dict[str, float] = defaultdict(time.time)
        self._lock = threading.Lock()
    
    def is_allowed(self, key: str) -> bool:
        with self._lock:
            now = time.time()
            elapsed = now - self._last_update[key]
            
            self._tokens[key] = min(
                self.requests_per_second,
                self._tokens[key] + elapsed * self.requests_per_second
            )
            self._last_update[key] = now
            
            if self._tokens[key] >= 1:
                self._tokens[key] -= 1
                return True
            
            return False

class ServiceMeshProxy:
    def __init__(self):
        self.registry = ServiceRegistry()
        self.load_balancer = LoadBalancer()
        self.circuit_breaker = CircuitBreaker()
        self.rate_limiter = RateLimiter()
        self._interceptors: List[Callable] = []
    
    def add_interceptor(self, interceptor: Callable):
        self._interceptors.append(interceptor)
    
    def register_service(self, instance: ServiceInstance):
        self.registry.register(instance)
    
    def route(
        self,
        service_name: str,
        request: Dict[str, Any],
        lb_strategy: str = "round_robin"
    ) -> Dict[str, Any]:
        rate_key = f"rate:{service_name}"
        if not self.rate_limiter.is_allowed(rate_key):
            return {'error': 'Rate limit exceeded', 'status': 429}
        
        instances = self.registry.get_instances(service_name)
        if not instances:
            return {'error': 'Service not available', 'status': 503}
        
        instance = self.load_balancer.select(instances, lb_strategy)
        if not instance:
            return {'error': 'No available instance', 'status': 503}
        
        cb_key = f"cb:{instance.instance_id}"
        if not self.circuit_breaker.is_allowed(cb_key):
            return {'error': 'Circuit breaker open', 'status': 503}
        
        for interceptor in self._interceptors:
            try:
                request = interceptor(request)
            except:
                pass
        
        try:
            response = self._forward_request(instance, request)
            self.circuit_breaker.record_success(cb_key)
            return response
        except Exception as e:
            self.circuit_breaker.record_failure(cb_key)
            return {'error': str(e), 'status': 500}
    
    def _forward_request(self, instance: ServiceInstance, request: Dict[str, Any]) -> Dict[str, Any]:
        time.sleep(0.01)
        
        if random.random() < 0.1:
            raise Exception("Connection refused")
        
        return {
            'status': 200,
            'data': f"Response from {instance.host}:{instance.port}",
            'request': request
        }
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'services': {
                name: len(instances)
                for name, instances in self.registry.services.items()
            }
        }

def main():
    proxy = ServiceMeshProxy()
    
    proxy.register_service(ServiceInstance("user-1", "user-service", "192.168.1.10", 8001))
    proxy.register_service(ServiceInstance("user-2", "user-service", "192.168.1.11", 8001))
    proxy.register_service(ServiceInstance("order-1", "order-service", "192.168.1.20", 8002))
    
    def logging_interceptor(request):
        print(f"  [拦截器] 请求: {request.get('path', '/')}")
        return request
    
    proxy.add_interceptor(logging_interceptor)
    
    print("路由请求到 user-service:")
    for i in range(5):
        response = proxy.route("user-service", {"path": "/api/users", "method": "GET"})
        print(f"  响应: {response.get('status')} - {response.get('data', response.get('error'))}")
    
    print("\n路由请求到 order-service:")
    response = proxy.route("order-service", {"path": "/api/orders", "method": "POST"})
    print(f"  响应: {response}")
    
    print(f"\n代理统计: {proxy.get_stats()}")

if __name__ == "__main__":
    main()
