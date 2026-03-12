# -----------------------------
# 题目：实现分布式API网关。
# 描述：支持路由转发、负载均衡、熔断限流。
# -----------------------------

import time
import threading
import random
import hashlib
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

@dataclass
class Route:
    path_pattern: str
    service_name: str
    strip_prefix: bool = False
    rate_limit: int = 100
    timeout: float = 30.0
    retry_count: int = 3

@dataclass
class CircuitBreakerState:
    failures: int = 0
    last_failure: float = 0
    state: str = "closed"

class ServiceRegistry:
    def __init__(self):
        self.services: Dict[str, List[ServiceInstance]] = defaultdict(list)
        self._lock = threading.Lock()
    
    def register(self, instance: ServiceInstance):
        with self._lock:
            self.services[instance.service_name].append(instance)
    
    def deregister(self, service_name: str, instance_id: str):
        with self._lock:
            self.services[service_name] = [
                i for i in self.services[service_name]
                if i.instance_id != instance_id
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
            total = sum(i.weight for i in instances)
            r = random.uniform(0, total)
            current = 0
            for inst in instances:
                current += inst.weight
                if current >= r:
                    return inst
            return instances[-1]
        
        return instances[0]

class RateLimiter:
    def __init__(self):
        self._tokens: Dict[str, List[float]] = defaultdict(list)
        self._lock = threading.Lock()
    
    def is_allowed(self, key: str, limit: int, window: float = 1.0) -> bool:
        with self._lock:
            now = time.time()
            cutoff = now - window
            
            self._tokens[key] = [t for t in self._tokens[key] if t > cutoff]
            
            if len(self._tokens[key]) < limit:
                self._tokens[key].append(now)
                return True
            
            return False

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
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
                    return True
                return False
            
            return True
    
    def record_success(self, key: str):
        with self._lock:
            self._states[key].failures = 0
            self._states[key].state = "closed"
    
    def record_failure(self, key: str):
        with self._lock:
            state = self._states[key]
            state.failures += 1
            state.last_failure = time.time()
            
            if state.failures >= self.failure_threshold:
                state.state = "open"

class APIGateway:
    def __init__(self):
        self.registry = ServiceRegistry()
        self.load_balancer = LoadBalancer()
        self.rate_limiter = RateLimiter()
        self.circuit_breaker = CircuitBreaker()
        self.routes: List[Route] = []
        self._middleware: List[Callable] = []
        self._request_counter = 0
        self._lock = threading.Lock()
    
    def add_route(self, route: Route):
        self.routes.append(route)
    
    def add_middleware(self, middleware: Callable):
        self._middleware.append(middleware)
    
    def register_service(self, instance: ServiceInstance):
        self.registry.register(instance)
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            self._request_counter += 1
            request_id = f"req-{self._request_counter}"
        
        request['request_id'] = request_id
        
        for middleware in self._middleware:
            result = middleware(request)
            if result:
                return result
        
        route = self._match_route(request.get('path', ''))
        if not route:
            return {'status': 404, 'error': 'Not Found'}
        
        rate_key = f"rate:{route.service_name}:{request.get('client_ip', 'default')}"
        if not self.rate_limiter.is_allowed(rate_key, route.rate_limit):
            return {'status': 429, 'error': 'Too Many Requests'}
        
        instances = self.registry.get_instances(route.service_name)
        if not instances:
            return {'status': 503, 'error': 'Service Unavailable'}
        
        instance = self.load_balancer.select(instances)
        if not instance:
            return {'status': 503, 'error': 'No Available Instance'}
        
        cb_key = f"cb:{instance.instance_id}"
        if not self.circuit_breaker.is_allowed(cb_key):
            return {'status': 503, 'error': 'Circuit Breaker Open'}
        
        try:
            response = self._forward_request(instance, request, route)
            self.circuit_breaker.record_success(cb_key)
            return response
        except Exception as e:
            self.circuit_breaker.record_failure(cb_key)
            return {'status': 500, 'error': str(e)}
    
    def _match_route(self, path: str) -> Optional[Route]:
        for route in self.routes:
            if path.startswith(route.path_pattern):
                return route
        return None
    
    def _forward_request(
        self,
        instance: ServiceInstance,
        request: Dict[str, Any],
        route: Route
    ) -> Dict[str, Any]:
        time.sleep(0.01)
        
        if random.random() < 0.05:
            raise Exception("Connection refused")
        
        return {
            'status': 200,
            'data': {
                'service': instance.service_name,
                'instance': f"{instance.host}:{instance.port}",
                'request_id': request.get('request_id')
            }
        }
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'total_requests': self._request_counter,
            'services': {
                name: len(instances)
                for name, instances in self.registry.services.items()
            },
            'routes': len(self.routes)
        }

def main():
    gateway = APIGateway()
    
    gateway.add_route(Route(
        path_pattern="/api/users",
        service_name="user-service",
        rate_limit=10
    ))
    
    gateway.add_route(Route(
        path_pattern="/api/orders",
        service_name="order-service",
        rate_limit=5
    ))
    
    gateway.register_service(ServiceInstance("user-1", "user-service", "192.168.1.10", 8001))
    gateway.register_service(ServiceInstance("user-2", "user-service", "192.168.1.11", 8001))
    gateway.register_service(ServiceInstance("order-1", "order-service", "192.168.1.20", 8002))
    
    def auth_middleware(request):
        token = request.get('headers', {}).get('Authorization')
        if not token:
            return {'status': 401, 'error': 'Unauthorized'}
        return None
    
    gateway.add_middleware(auth_middleware)
    
    print("处理请求...")
    for i in range(5):
        request = {
            'path': '/api/users/123',
            'method': 'GET',
            'headers': {'Authorization': 'Bearer token123'},
            'client_ip': '192.168.1.100'
        }
        
        response = gateway.handle_request(request)
        print(f"请求 {i+1}: {response['status']} - {response.get('data', response.get('error'))}")
    
    print("\n无认证请求:")
    request = {'path': '/api/users/123', 'method': 'GET', 'headers': {}}
    response = gateway.handle_request(request)
    print(f"响应: {response}")
    
    print(f"\n网关统计: {gateway.get_stats()}")

if __name__ == "__main__":
    main()
