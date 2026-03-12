# -----------------------------
# 题目：实现服务注册与发现中心。
# 描述：支持服务注册、健康检查、负载均衡。
# -----------------------------

import time
import threading
import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

class ServiceStatus(Enum):
    UP = "up"
    DOWN = "down"
    STARTING = "starting"
    OUT_OF_SERVICE = "out_of_service"

@dataclass
class ServiceInstance:
    instance_id: str
    service_name: str
    host: str
    port: int
    status: ServiceStatus = ServiceStatus.UP
    metadata: Dict[str, str] = field(default_factory=dict)
    last_heartbeat: float = field(default_factory=time.time)
    registration_time: float = field(default_factory=time.time)
    weight: int = 1

@dataclass
class Service:
    service_name: str
    instances: Dict[str, ServiceInstance] = field(default_factory=dict)
    
    def get_healthy_instances(self) -> List[ServiceInstance]:
        return [
            inst for inst in self.instances.values()
            if inst.status == ServiceStatus.UP
        ]

class LoadBalancer:
    def __init__(self):
        self._counters: Dict[str, int] = defaultdict(int)
    
    def round_robin(self, instances: List[ServiceInstance]) -> Optional[ServiceInstance]:
        if not instances:
            return None
        
        service_name = instances[0].service_name
        idx = self._counters[service_name] % len(instances)
        self._counters[service_name] += 1
        return instances[idx]
    
    def random(self, instances: List[ServiceInstance]) -> Optional[ServiceInstance]:
        if not instances:
            return None
        return random.choice(instances)
    
    def weighted_random(self, instances: List[ServiceInstance]) -> Optional[ServiceInstance]:
        if not instances:
            return None
        
        total_weight = sum(inst.weight for inst in instances)
        if total_weight == 0:
            return random.choice(instances)
        
        r = random.uniform(0, total_weight)
        current_weight = 0
        
        for inst in instances:
            current_weight += inst.weight
            if current_weight >= r:
                return inst
        
        return instances[-1]
    
    def least_connections(self, instances: List[ServiceInstance]) -> Optional[ServiceInstance]:
        if not instances:
            return None
        
        return min(instances, key=lambda x: x.metadata.get('connections', 0))

class ServiceRegistry:
    def __init__(self, heartbeat_timeout: float = 30.0):
        self.services: Dict[str, Service] = {}
        self.heartbeat_timeout = heartbeat_timeout
        self.load_balancer = LoadBalancer()
        self._lock = threading.RLock()
        self._running = False
        self._eviction_thread: Optional[threading.Thread] = None
    
    def register(self, instance: ServiceInstance) -> bool:
        with self._lock:
            if instance.service_name not in self.services:
                self.services[instance.service_name] = Service(instance.service_name)
            
            self.services[instance.service_name].instances[instance.instance_id] = instance
            return True
    
    def deregister(self, service_name: str, instance_id: str) -> bool:
        with self._lock:
            service = self.services.get(service_name)
            if service and instance_id in service.instances:
                del service.instances[instance_id]
                return True
            return False
    
    def heartbeat(self, service_name: str, instance_id: str) -> bool:
        with self._lock:
            service = self.services.get(service_name)
            if service and instance_id in service.instances:
                instance = service.instances[instance_id]
                instance.last_heartbeat = time.time()
                instance.status = ServiceStatus.UP
                return True
            return False
    
    def get_instances(self, service_name: str) -> List[ServiceInstance]:
        with self._lock:
            service = self.services.get(service_name)
            if service:
                return service.get_healthy_instances()
            return []
    
    def get_instance(
        self,
        service_name: str,
        strategy: str = "round_robin"
    ) -> Optional[ServiceInstance]:
        instances = self.get_instances(service_name)
        
        if strategy == "round_robin":
            return self.load_balancer.round_robin(instances)
        elif strategy == "random":
            return self.load_balancer.random(instances)
        elif strategy == "weighted":
            return self.load_balancer.weighted_random(instances)
        else:
            return self.load_balancer.round_robin(instances)
    
    def start_eviction(self, interval: float = 10.0):
        self._running = True
        self._eviction_thread = threading.Thread(
            target=self._eviction_loop,
            args=(interval,)
        )
        self._eviction_thread.daemon = True
        self._eviction_thread.start()
    
    def stop_eviction(self):
        self._running = False
        if self._eviction_thread:
            self._eviction_thread.join(timeout=5.0)
    
    def _eviction_loop(self, interval: float):
        while self._running:
            self._evict_expired_instances()
            time.sleep(interval)
    
    def _evict_expired_instances(self):
        now = time.time()
        with self._lock:
            for service in self.services.values():
                expired = [
                    inst_id for inst_id, inst in service.instances.items()
                    if now - inst.last_heartbeat > self.heartbeat_timeout
                ]
                
                for inst_id in expired:
                    service.instances[inst_id].status = ServiceStatus.DOWN
    
    def get_all_services(self) -> Dict[str, List[Dict[str, Any]]]:
        with self._lock:
            return {
                name: [
                    {
                        'instance_id': inst.instance_id,
                        'host': inst.host,
                        'port': inst.port,
                        'status': inst.status.value
                    }
                    for inst in service.instances.values()
                ]
                for name, service in self.services.items()
            }

class ServiceDiscoveryClient:
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        self._local_cache: Dict[str, List[ServiceInstance]] = {}
        self._cache_time: Dict[str, float] = {}
        self._cache_ttl = 10.0
    
    def register_service(
        self,
        service_name: str,
        host: str,
        port: int,
        metadata: Dict = None
    ) -> str:
        import uuid
        instance_id = f"{service_name}-{uuid.uuid4().hex[:8]}"
        
        instance = ServiceInstance(
            instance_id=instance_id,
            service_name=service_name,
            host=host,
            port=port,
            metadata=metadata or {}
        )
        
        self.registry.register(instance)
        return instance_id
    
    def discover(self, service_name: str) -> List[ServiceInstance]:
        now = time.time()
        
        if service_name in self._local_cache:
            if now - self._cache_time.get(service_name, 0) < self._cache_ttl:
                return self._local_cache[service_name]
        
        instances = self.registry.get_instances(service_name)
        self._local_cache[service_name] = instances
        self._cache_time[service_name] = now
        
        return instances
    
    def get_service_url(self, service_name: str) -> Optional[str]:
        instance = self.registry.get_instance(service_name)
        if instance:
            return f"http://{instance.host}:{instance.port}"
        return None

def main():
    registry = ServiceRegistry(heartbeat_timeout=10.0)
    registry.start_eviction()
    
    client = ServiceDiscoveryClient(registry)
    
    print("注册服务...")
    client.register_service("user-service", "192.168.1.10", 8001)
    client.register_service("user-service", "192.168.1.11", 8001)
    client.register_service("order-service", "192.168.1.20", 8002)
    
    print("\n发现服务:")
    user_instances = client.discover("user-service")
    for inst in user_instances:
        print(f"  {inst.service_name}: {inst.host}:{inst.port}")
    
    print("\n负载均衡:")
    for i in range(5):
        url = client.get_service_url("user-service")
        print(f"  请求 {i+1}: {url}")
    
    print("\n所有服务:")
    for name, instances in registry.get_all_services().items():
        print(f"  {name}: {len(instances)} 个实例")
    
    registry.stop_eviction()

if __name__ == "__main__":
    main()
