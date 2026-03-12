# -----------------------------
# 题目：实现简单的服务网格。
# 描述：支持服务发现、负载均衡、熔断。
# -----------------------------

import time
import threading
import random
from collections import defaultdict
from enum import Enum

class ServiceStatus(Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"

class ServiceInstance:
    def __init__(self, service_id, host, port):
        self.service_id = service_id
        self.host = host
        self.port = port
        self.status = ServiceStatus.HEALTHY
        self.last_check = time.time()
        self.request_count = 0
        self.error_count = 0

class ServiceRegistry:
    def __init__(self):
        self.services = defaultdict(dict)
        self._lock = threading.Lock()
    
    def register(self, service_name, instance):
        with self._lock:
            self.services[service_name][instance.service_id] = instance
    
    def deregister(self, service_name, instance_id):
        with self._lock:
            self.services[service_name].pop(instance_id, None)
    
    def get_instances(self, service_name):
        with self._lock:
            return list(self.services[service_name].values())

class LoadBalancer:
    def __init__(self, registry):
        self.registry = registry
        self.counters = defaultdict(int)
    
    def round_robin(self, service_name):
        instances = self.registry.get_instances(service_name)
        healthy = [i for i in instances if i.status == ServiceStatus.HEALTHY]
        if not healthy:
            return None
        self.counters[service_name] = (self.counters[service_name] + 1) % len(healthy)
        return healthy[self.counters[service_name]]
    
    def random(self, service_name):
        instances = self.registry.get_instances(service_name)
        healthy = [i for i in instances if i.status == ServiceStatus.HEALTHY]
        return random.choice(healthy) if healthy else None
    
    def least_connections(self, service_name):
        instances = self.registry.get_instances(service_name)
        healthy = [i for i in instances if i.status == ServiceStatus.HEALTHY]
        if not healthy:
            return None
        return min(healthy, key=lambda x: x.request_count)

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = defaultdict(int)
        self.open_time = defaultdict(float)
        self._lock = threading.Lock()
    
    def is_open(self, service_id):
        with self._lock:
            if self.failures[service_id] >= self.failure_threshold:
                if time.time() - self.open_time[service_id] < self.recovery_timeout:
                    return True
                self.failures[service_id] = 0
            return False
    
    def record_success(self, service_id):
        with self._lock:
            self.failures[service_id] = 0
    
    def record_failure(self, service_id):
        with self._lock:
            self.failures[service_id] += 1
            if self.failures[service_id] >= self.failure_threshold:
                self.open_time[service_id] = time.time()

class ServiceMesh:
    def __init__(self):
        self.registry = ServiceRegistry()
        self.load_balancer = LoadBalancer(self.registry)
        self.circuit_breaker = CircuitBreaker()
    
    def register(self, service_name, instance):
        self.registry.register(service_name, instance)
    
    def call(self, service_name):
        instance = self.load_balancer.round_robin(service_name)
        if not instance:
            raise Exception("无可用实例")
        
        if self.circuit_breaker.is_open(instance.service_id):
            raise Exception("熔断器打开")
        
        instance.request_count += 1
        return instance
    
    def record_success(self, instance):
        self.circuit_breaker.record_success(instance.service_id)
    
    def record_failure(self, instance):
        self.circuit_breaker.record_failure(instance.service_id)
        instance.error_count += 1

def main():
    mesh = ServiceMesh()
    
    mesh.register('user-service', ServiceInstance('user-1', '192.168.1.1', 8001))
    mesh.register('user-service', ServiceInstance('user-2', '192.168.1.2', 8001))
    mesh.register('user-service', ServiceInstance('user-3', '192.168.1.3', 8001))
    
    for i in range(5):
        instance = mesh.call('user-service')
        print(f"调用 {i+1}: {instance.service_id} -> {instance.host}:{instance.port}")


if __name__ == "__main__":
    main()
