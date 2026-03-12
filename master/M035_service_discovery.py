# -----------------------------
# 题目：实现服务注册与发现。
# 描述：支持服务注册、心跳检测、负载均衡。
# -----------------------------

import time
import threading
import random
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

class ServiceStatus(Enum):
    UP = "UP"
    DOWN = "DOWN"
    STARTING = "STARTING"
    OUT_OF_SERVICE = "OUT_OF_SERVICE"

@dataclass
class ServiceInstance:
    instance_id: str
    service_name: str
    host: str
    port: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: ServiceStatus = ServiceStatus.UP
    last_heartbeat: float = field(default_factory=time.time)
    registration_time: float = field(default_factory=time.time)
    weight: int = 1

class ServiceRegistry:
    def __init__(self, heartbeat_timeout: float = 30.0, eviction_interval: float = 60.0):
        self._instances: Dict[str, Dict[str, ServiceInstance]] = defaultdict(dict)
        self._heartbeat_timeout = heartbeat_timeout
        self._eviction_interval = eviction_interval
        self._lock = threading.RLock()
        self._running = False
        self._eviction_thread: Optional[threading.Thread] = None
    
    def register(self, instance: ServiceInstance) -> bool:
        with self._lock:
            self._instances[instance.service_name][instance.instance_id] = instance
            return True
    
    def deregister(self, service_name: str, instance_id: str) -> bool:
        with self._lock:
            if service_name in self._instances:
                return self._instances[service_name].pop(instance_id, None) is not None
            return False
    
    def heartbeat(self, service_name: str, instance_id: str) -> bool:
        with self._lock:
            instances = self._instances.get(service_name)
            if instances and instance_id in instances:
                instances[instance_id].last_heartbeat = time.time()
                instances[instance_id].status = ServiceStatus.UP
                return True
            return False
    
    def get_instances(self, service_name: str) -> List[ServiceInstance]:
        with self._lock:
            instances = self._instances.get(service_name, {})
            return [
                inst for inst in instances.values()
                if inst.status == ServiceStatus.UP
            ]
    
    def get_all_services(self) -> Dict[str, List[Dict[str, Any]]]:
        with self._lock:
            result = {}
            for service_name, instances in self._instances.items():
                result[service_name] = [
                    {
                        'instance_id': inst.instance_id,
                        'host': inst.host,
                        'port': inst.port,
                        'status': inst.status.value,
                        'metadata': inst.metadata
                    }
                    for inst in instances.values()
                ]
            return result
    
    def start_eviction(self):
        self._running = True
        self._eviction_thread = threading.Thread(target=self._eviction_loop)
        self._eviction_thread.daemon = True
        self._eviction_thread.start()
    
    def stop_eviction(self):
        self._running = False
        if self._eviction_thread:
            self._eviction_thread.join(timeout=2.0)
    
    def _eviction_loop(self):
        while self._running:
            self._evict_expired_instances()
            time.sleep(self._eviction_interval)
    
    def _evict_expired_instances(self):
        now = time.time()
        with self._lock:
            for service_name in list(self._instances.keys()):
                instances = self._instances[service_name]
                expired_ids = [
                    inst_id for inst_id, inst in instances.items()
                    if now - inst.last_heartbeat > self._heartbeat_timeout
                ]
                for inst_id in expired_ids:
                    del instances[inst_id]

class LoadBalancer:
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        self._counters: Dict[str, int] = defaultdict(int)
    
    def select_instance(self, service_name: str, strategy: str = "round_robin") -> Optional[ServiceInstance]:
        instances = self.registry.get_instances(service_name)
        if not instances:
            return None
        
        if strategy == "round_robin":
            return self._round_robin(service_name, instances)
        elif strategy == "random":
            return self._random(instances)
        elif strategy == "weighted":
            return self._weighted(instances)
        elif strategy == "least_connections":
            return self._least_connections(instances)
        
        return instances[0]
    
    def _round_robin(self, service_name: str, instances: List[ServiceInstance]) -> ServiceInstance:
        index = self._counters[service_name] % len(instances)
        self._counters[service_name] += 1
        return instances[index]
    
    def _random(self, instances: List[ServiceInstance]) -> ServiceInstance:
        return random.choice(instances)
    
    def _weighted(self, instances: List[ServiceInstance]) -> ServiceInstance:
        total_weight = sum(inst.weight for inst in instances)
        r = random.randint(1, total_weight)
        
        current_weight = 0
        for inst in instances:
            current_weight += inst.weight
            if current_weight >= r:
                return inst
        
        return instances[-1]
    
    def _least_connections(self, instances: List[ServiceInstance]) -> ServiceInstance:
        return min(instances, key=lambda x: x.metadata.get('connections', 0))

class ServiceDiscovery:
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        self._local_cache: Dict[str, List[ServiceInstance]] = {}
        self._cache_time: Dict[str, float] = {}
        self._cache_ttl = 10.0
        self._lock = threading.Lock()
    
    def discover(self, service_name: str, use_cache: bool = True) -> List[ServiceInstance]:
        if use_cache:
            cached = self._get_from_cache(service_name)
            if cached is not None:
                return cached
        
        instances = self.registry.get_instances(service_name)
        self._update_cache(service_name, instances)
        return instances
    
    def _get_from_cache(self, service_name: str) -> Optional[List[ServiceInstance]]:
        with self._lock:
            if service_name in self._local_cache:
                cache_time = self._cache_time.get(service_name, 0)
                if time.time() - cache_time < self._cache_ttl:
                    return self._local_cache[service_name]
        return None
    
    def _update_cache(self, service_name: str, instances: List[ServiceInstance]):
        with self._lock:
            self._local_cache[service_name] = instances
            self._cache_time[service_name] = time.time()
    
    def invalidate_cache(self, service_name: str = None):
        with self._lock:
            if service_name:
                self._local_cache.pop(service_name, None)
                self._cache_time.pop(service_name, None)
            else:
                self._local_cache.clear()
                self._cache_time.clear()

class ServiceClient:
    def __init__(self, discovery: ServiceDiscovery, load_balancer: LoadBalancer):
        self.discovery = discovery
        self.load_balancer = load_balancer
    
    def get_service_url(self, service_name: str) -> Optional[str]:
        instance = self.load_balancer.select_instance(service_name)
        if instance:
            return f"http://{instance.host}:{instance.port}"
        return None
    
    def call_service(self, service_name: str, path: str) -> Optional[str]:
        url = self.get_service_url(service_name)
        if url:
            return f"{url}{path}"
        return None

def main():
    registry = ServiceRegistry(heartbeat_timeout=60.0)
    registry.start_eviction()
    
    registry.register(ServiceInstance(
        instance_id="user-service-1",
        service_name="user-service",
        host="192.168.1.1",
        port=8001,
        weight=3
    ))
    
    registry.register(ServiceInstance(
        instance_id="user-service-2",
        service_name="user-service",
        host="192.168.1.2",
        port=8001,
        weight=2
    ))
    
    registry.register(ServiceInstance(
        instance_id="order-service-1",
        service_name="order-service",
        host="192.168.1.3",
        port=8002
    ))
    
    print("已注册服务:")
    for service_name, instances in registry.get_all_services().items():
        print(f"  {service_name}: {len(instances)} 个实例")
    
    load_balancer = LoadBalancer(registry)
    discovery = ServiceDiscovery(registry)
    
    print("\n负载均衡选择:")
    for i in range(5):
        instance = load_balancer.select_instance("user-service", strategy="weighted")
        if instance:
            print(f"  请求 {i+1}: {instance.host}:{instance.port}")
    
    client = ServiceClient(discovery, load_balancer)
    url = client.get_service_url("user-service")
    print(f"\n服务URL: {url}")
    
    registry.stop_eviction()

if __name__ == "__main__":
    main()
