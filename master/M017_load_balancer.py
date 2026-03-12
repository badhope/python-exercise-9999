# -----------------------------
# 题目：实现负载均衡器。
# 描述：支持多种负载均衡策略，健康检查。
# -----------------------------

import time
import random
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from threading import Lock

@dataclass
class ServiceInstance:
    instance_id: str
    host: str
    port: int
    weight: int = 1
    status: str = 'UP'
    last_check: float = 0
    request_count: int = 0

class LoadBalanceStrategy(ABC):
    @abstractmethod
    def select(self, instances: List[ServiceInstance]) -> Optional[ServiceInstance]:
        pass

class RoundRobinStrategy(LoadBalanceStrategy):
    def __init__(self):
        self.counter = 0
        self._lock = Lock()
    
    def select(self, instances: List[ServiceInstance]) -> Optional[ServiceInstance]:
        if not instances:
            return None
        
        with self._lock:
            self.counter = (self.counter + 1) % len(instances)
            return instances[self.counter]

class WeightedRoundRobinStrategy(LoadBalanceStrategy):
    def __init__(self):
        self.current_weights: Dict[str, int] = {}
        self._lock = Lock()
    
    def select(self, instances: List[ServiceInstance]) -> Optional[ServiceInstance]:
        if not instances:
            return None
        
        with self._lock:
            for instance in instances:
                if instance.instance_id not in self.current_weights:
                    self.current_weights[instance.instance_id] = 0
                self.current_weights[instance.instance_id] += instance.weight
            
            max_weight = -1
            selected = None
            for instance in instances:
                if self.current_weights[instance.instance_id] > max_weight:
                    max_weight = self.current_weights[instance.instance_id]
                    selected = instance
            
            if selected:
                self.current_weights[selected.instance_id] -= sum(i.weight for i in instances)
            
            return selected

class LeastConnectionsStrategy(LoadBalanceStrategy):
    def select(self, instances: List[ServiceInstance]) -> Optional[ServiceInstance]:
        if not instances:
            return None
        
        return min(instances, key=lambda x: x.request_count)

class RandomStrategy(LoadBalanceStrategy):
    def select(self, instances: List[ServiceInstance]) -> Optional[ServiceInstance]:
        if not instances:
            return None
        return random.choice(instances)

class ConsistentHashStrategy(LoadBalanceStrategy):
    def __init__(self, virtual_nodes: int = 150):
        self.virtual_nodes = virtual_nodes
        self.ring: Dict[int, ServiceInstance] = {}
        self.sorted_keys: List[int] = []
    
    def _hash(self, key: str) -> int:
        return hash(key) & 0xffffffff
    
    def add_instance(self, instance: ServiceInstance):
        for i in range(self.virtual_nodes):
            key = self._hash(f"{instance.instance_id}#{i}")
            self.ring[key] = instance
        
        self.sorted_keys = sorted(self.ring.keys())
    
    def remove_instance(self, instance: ServiceInstance):
        for i in range(self.virtual_nodes):
            key = self._hash(f"{instance.instance_id}#{i}")
            self.ring.pop(key, None)
        
        self.sorted_keys = sorted(self.ring.keys())
    
    def select(self, instances: List[ServiceInstance]) -> Optional[ServiceInstance]:
        return self.select_with_key(str(time.time()))
    
    def select_with_key(self, key: str) -> Optional[ServiceInstance]:
        if not self.ring:
            return None
        
        hash_key = self._hash(key)
        
        for ring_key in self.sorted_keys:
            if hash_key <= ring_key:
                return self.ring[ring_key]
        
        return self.ring[self.sorted_keys[0]]

class HealthChecker:
    def __init__(self, check_interval: float = 30.0):
        self.check_interval = check_interval
    
    def check(self, instance: ServiceInstance) -> bool:
        now = time.time()
        if now - instance.last_check < self.check_interval:
            return instance.status == 'UP'
        
        instance.last_check = now
        import random
        is_healthy = random.random() > 0.1
        instance.status = 'UP' if is_healthy else 'DOWN'
        return is_healthy

class LoadBalancer:
    def __init__(self, strategy: LoadBalanceStrategy = None):
        self.instances: List[ServiceInstance] = []
        self.strategy = strategy or RoundRobinStrategy()
        self.health_checker = HealthChecker()
        self._lock = Lock()
    
    def add_instance(self, instance: ServiceInstance):
        with self._lock:
            self.instances.append(instance)
            if isinstance(self.strategy, ConsistentHashStrategy):
                self.strategy.add_instance(instance)
    
    def remove_instance(self, instance_id: str):
        with self._lock:
            instance = next((i for i in self.instances if i.instance_id == instance_id), None)
            if instance:
                self.instances.remove(instance)
                if isinstance(self.strategy, ConsistentHashStrategy):
                    self.strategy.remove_instance(instance)
    
    def select_instance(self) -> Optional[ServiceInstance]:
        with self._lock:
            healthy_instances = [
                i for i in self.instances
                if self.health_checker.check(i)
            ]
            
            if not healthy_instances:
                return None
            
            selected = self.strategy.select(healthy_instances)
            if selected:
                selected.request_count += 1
            
            return selected
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'total_instances': len(self.instances),
            'healthy_instances': sum(1 for i in self.instances if i.status == 'UP'),
            'total_requests': sum(i.request_count for i in self.instances)
        }

def main():
    lb = LoadBalancer(RoundRobinStrategy())
    
    lb.add_instance(ServiceInstance("inst-1", "192.168.1.1", 8001, weight=3))
    lb.add_instance(ServiceInstance("inst-2", "192.168.1.2", 8001, weight=2))
    lb.add_instance(ServiceInstance("inst-3", "192.168.1.3", 8001, weight=1))
    
    for i in range(10):
        instance = lb.select_instance()
        if instance:
            print(f"请求 {i+1}: {instance.instance_id} ({instance.host}:{instance.port})")
    
    print(f"\n统计信息: {lb.get_stats()}")

if __name__ == "__main__":
    main()
