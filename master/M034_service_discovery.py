# -----------------------------
# 题目：实现服务发现。
# -----------------------------

import threading
import time
from collections import defaultdict

class ServiceInstance:
    def __init__(self, service_id, host, port, metadata=None):
        self.service_id = service_id
        self.host = host
        self.port = port
        self.metadata = metadata or {}
        self.last_heartbeat = time.time()
        self.health_check_url = None
    
    def is_healthy(self, ttl=30):
        return time.time() - self.last_heartbeat < ttl

class ServiceRegistry:
    def __init__(self):
        self.services = defaultdict(list)
        self.lock = threading.Lock()
    
    def register(self, service_name, instance):
        with self.lock:
            for existing in self.services[service_name]:
                if existing.service_id == instance.service_id:
                    return False
            self.services[service_name].append(instance)
            return True
    
    def deregister(self, service_name, service_id):
        with self.lock:
            self.services[service_name] = [
                s for s in self.services[service_name]
                if s.service_id != service_id
            ]
    
    def discover(self, service_name):
        with self.lock:
            instances = self.services.get(service_name, [])
            return [s for s in instances if s.is_healthy()]
    
    def heartbeat(self, service_name, service_id):
        with self.lock:
            for instance in self.services.get(service_name, []):
                if instance.service_id == service_id:
                    instance.last_heartbeat = time.time()
                    return True
        return False

if __name__ == "__main__":
    registry = ServiceRegistry()
    
    instance1 = ServiceInstance("inst-1", "localhost", 8001, {"version": "1.0"})
    instance2 = ServiceInstance("inst-2", "localhost", 8002, {"version": "1.0"})
    
    registry.register("user-service", instance1)
    registry.register("user-service", instance2)
    
    instances = registry.discover("user-service")
    print(f"Found {len(instances)} instances")
    
    for inst in instances:
        print(f"  - {inst.host}:{inst.port}")
