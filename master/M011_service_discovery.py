# -----------------------------
# 题目：实现简单的服务发现。
# 描述：支持服务注册、发现、健康检查。
# -----------------------------

import time
import threading

class ServiceInstance:
    def __init__(self, service_id, host, port, metadata=None):
        self.service_id = service_id
        self.host = host
        self.port = port
        self.metadata = metadata or {}
        self.last_heartbeat = time.time()
        self.status = 'UP'

class ServiceRegistry:
    def __init__(self, heartbeat_timeout=30):
        self.services = {}
        self.heartbeat_timeout = heartbeat_timeout
        self._lock = threading.Lock()
    
    def register(self, service_name, instance):
        with self._lock:
            if service_name not in self.services:
                self.services[service_name] = {}
            self.services[service_name][instance.service_id] = instance
    
    def deregister(self, service_name, instance_id):
        with self._lock:
            if service_name in self.services:
                self.services[service_name].pop(instance_id, None)
    
    def heartbeat(self, service_name, instance_id):
        with self._lock:
            if service_name in self.services:
                instance = self.services[service_name].get(instance_id)
                if instance:
                    instance.last_heartbeat = time.time()
    
    def get_instances(self, service_name):
        with self._lock:
            instances = self.services.get(service_name, {})
            return [i for i in instances.values() if i.status == 'UP']
    
    def check_health(self):
        with self._lock:
            now = time.time()
            for service_name, instances in self.services.items():
                for instance in instances.values():
                    if now - instance.last_heartbeat > self.heartbeat_timeout:
                        instance.status = 'DOWN'

class LoadBalancer:
    def __init__(self, registry):
        self.registry = registry
        self.counters = {}
    
    def get_instance(self, service_name):
        instances = self.registry.get_instances(service_name)
        if not instances:
            return None
        
        if service_name not in self.counters:
            self.counters[service_name] = 0
        
        self.counters[service_name] = (self.counters[service_name] + 1) % len(instances)
        return instances[self.counters[service_name]]

def main():
    registry = ServiceRegistry(heartbeat_timeout=60)
    
    registry.register('user-service', ServiceInstance('user-1', '192.168.1.1', 8001))
    registry.register('user-service', ServiceInstance('user-2', '192.168.1.2', 8001))
    registry.register('order-service', ServiceInstance('order-1', '192.168.1.3', 8002))
    
    lb = LoadBalancer(registry)
    
    for _ in range(4):
        instance = lb.get_instance('user-service')
        print(f"选择实例: {instance.service_id} -> {instance.host}:{instance.port}")


if __name__ == "__main__":
    main()
