"""
N049 - 分布式负载均衡
难度：Nightmare

题目描述：
实现一个分布式负载均衡系统，支持多种负载均衡算法（轮询、加权轮询、最少连接、一致性哈希）。
系统需要处理服务实例的健康检查、权重动态调整、流量分配和故障转移。

学习目标：
1. 理解各种负载均衡算法的原理和适用场景
2. 掌握服务实例的健康检查机制
3. 实现权重的动态调整
4. 处理故障转移和流量重分配

输入输出要求：
输入：服务请求（服务名称、请求参数）
输出：选中的服务实例和请求结果

预期解决方案：
使用不同的负载均衡策略，结合健康检查和权重调整实现高可用负载均衡。
"""

import hashlib
import random
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple


class InstanceStatus(Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DRAINING = "draining"


@dataclass
class ServiceInstance:
    instance_id: str
    host: str
    port: int
    weight: int = 1
    status: InstanceStatus = InstanceStatus.HEALTHY
    connections: int = 0
    total_requests: int = 0
    success_requests: int = 0
    failed_requests: int = 0
    last_check_time: float = 0
    response_time: float = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def address(self) -> str:
        return f"{self.host}:{self.port}"
    
    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 1.0
        return self.success_requests / self.total_requests


class LoadBalanceStrategy(ABC):
    @abstractmethod
    def select(self, instances: List[ServiceInstance]) -> Optional[ServiceInstance]:
        pass
    
    @abstractmethod
    def reset(self):
        pass


class RoundRobinStrategy(LoadBalanceStrategy):
    def __init__(self):
        self._index = 0
        self._lock = threading.Lock()
    
    def select(self, instances: List[ServiceInstance]) -> Optional[ServiceInstance]:
        if not instances:
            return None
        
        healthy = [i for i in instances if i.status == InstanceStatus.HEALTHY]
        if not healthy:
            return None
        
        with self._lock:
            instance = healthy[self._index % len(healthy)]
            self._index += 1
        
        return instance
    
    def reset(self):
        with self._lock:
            self._index = 0


class WeightedRoundRobinStrategy(LoadBalanceStrategy):
    def __init__(self):
        self._current_weights: Dict[str, int] = {}
        self._lock = threading.Lock()
    
    def select(self, instances: List[ServiceInstance]) -> Optional[ServiceInstance]:
        healthy = [i for i in instances if i.status == InstanceStatus.HEALTHY]
        if not healthy:
            return None
        
        with self._lock:
            for instance in healthy:
                if instance.instance_id not in self._current_weights:
                    self._current_weights[instance.instance_id] = 0
                self._current_weights[instance.instance_id] += instance.weight
            
            max_weight = -1
            selected = None
            
            for instance in healthy:
                weight = self._current_weights[instance.instance_id]
                if weight > max_weight:
                    max_weight = weight
                    selected = instance
            
            if selected:
                self._current_weights[selected.instance_id] -= sum(i.weight for i in healthy)
            
            return selected
    
    def reset(self):
        with self._lock:
            self._current_weights.clear()


class LeastConnectionsStrategy(LoadBalanceStrategy):
    def __init__(self):
        self._lock = threading.Lock()
    
    def select(self, instances: List[ServiceInstance]) -> Optional[ServiceInstance]:
        healthy = [i for i in instances if i.status == InstanceStatus.HEALTHY]
        if not healthy:
            return None
        
        with self._lock:
            return min(healthy, key=lambda x: x.connections)
    
    def reset(self):
        pass


class ConsistentHashStrategy(LoadBalanceStrategy):
    def __init__(self, virtual_nodes: int = 150):
        self.virtual_nodes = virtual_nodes
        self._ring: Dict[int, ServiceInstance] = {}
        self._sorted_keys: List[int] = []
        self._lock = threading.Lock()
    
    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
    
    def _build_ring(self, instances: List[ServiceInstance]):
        self._ring.clear()
        self._sorted_keys.clear()
        
        for instance in instances:
            for i in range(self.virtual_nodes):
                virtual_key = f"{instance.instance_id}#{i}"
                hash_key = self._hash(virtual_key)
                self._ring[hash_key] = instance
                self._sorted_keys.append(hash_key)
        
        self._sorted_keys.sort()
    
    def select(self, instances: List[ServiceInstance], key: str = None) -> Optional[ServiceInstance]:
        healthy = [i for i in instances if i.status == InstanceStatus.HEALTHY]
        if not healthy:
            return None
        
        with self._lock:
            self._build_ring(healthy)
            
            if not self._sorted_keys:
                return None
            
            if key is None:
                key = str(time.time())
            
            hash_key = self._hash(key)
            
            for ring_key in self._sorted_keys:
                if ring_key >= hash_key:
                    return self._ring[ring_key]
            
            return self._ring[self._sorted_keys[0]]
    
    def reset(self):
        with self._lock:
            self._ring.clear()
            self._sorted_keys.clear()


class HealthChecker:
    def __init__(self, check_interval: float = 10.0, timeout: float = 5.0):
        self.check_interval = check_interval
        self.timeout = timeout
        self._checkers: Dict[str, Callable] = {}
        self._running = False
        self._thread: Optional[threading.Thread] = None
    
    def register_checker(self, service_name: str, checker: Callable[[ServiceInstance], bool]):
        self._checkers[service_name] = checker
    
    def check(self, instance: ServiceInstance, service_name: str) -> bool:
        checker = self._checkers.get(service_name)
        if checker:
            try:
                return checker(instance)
            except Exception:
                return False
        
        return instance.status == InstanceStatus.HEALTHY


class LoadBalancer:
    def __init__(self, strategy: LoadBalanceStrategy = None):
        self._strategy = strategy or RoundRobinStrategy()
        self._services: Dict[str, List[ServiceInstance]] = {}
        self._health_checker = HealthChecker()
        self._lock = threading.RLock()
        self._listeners: List[Callable] = []
    
    def register_service(self, service_name: str, instances: List[ServiceInstance]):
        with self._lock:
            if service_name not in self._services:
                self._services[service_name] = []
            
            existing_ids = {i.instance_id for i in self._services[service_name]}
            
            for instance in instances:
                if instance.instance_id not in existing_ids:
                    self._services[service_name].append(instance)
    
    def deregister_instance(self, service_name: str, instance_id: str) -> bool:
        with self._lock:
            if service_name in self._services:
                for i, instance in enumerate(self._services[service_name]):
                    if instance.instance_id == instance_id:
                        del self._services[service_name][i]
                        return True
        return False
    
    def update_instance_weight(self, service_name: str, instance_id: str, weight: int) -> bool:
        with self._lock:
            if service_name in self._services:
                for instance in self._services[service_name]:
                    if instance.instance_id == instance_id:
                        instance.weight = weight
                        return True
        return False
    
    def select_instance(self, service_name: str, key: str = None) -> Optional[ServiceInstance]:
        with self._lock:
            instances = self._services.get(service_name, [])
            
            if isinstance(self._strategy, ConsistentHashStrategy):
                return self._strategy.select(instances, key)
            
            return self._strategy.select(instances)
    
    def record_request(self, service_name: str, instance_id: str, success: bool, response_time: float):
        with self._lock:
            if service_name in self._services:
                for instance in self._services[service_name]:
                    if instance.instance_id == instance_id:
                        instance.total_requests += 1
                        if success:
                            instance.success_requests += 1
                        else:
                            instance.failed_requests += 1
                        instance.response_time = (
                            instance.response_time * 0.9 + response_time * 0.1
                        )
                        break
    
    def acquire_connection(self, service_name: str, instance_id: str):
        with self._lock:
            if service_name in self._services:
                for instance in self._services[service_name]:
                    if instance.instance_id == instance_id:
                        instance.connections += 1
                        break
    
    def release_connection(self, service_name: str, instance_id: str):
        with self._lock:
            if service_name in self._services:
                for instance in self._services[service_name]:
                    if instance.instance_id == instance_id:
                        instance.connections = max(0, instance.connections - 1)
                        break
    
    def set_strategy(self, strategy: LoadBalanceStrategy):
        with self._lock:
            self._strategy = strategy
            self._strategy.reset()
    
    def get_instances(self, service_name: str) -> List[ServiceInstance]:
        with self._lock:
            return list(self._services.get(service_name, []))
    
    def get_healthy_instances(self, service_name: str) -> List[ServiceInstance]:
        with self._lock:
            instances = self._services.get(service_name, [])
            return [i for i in instances if i.status == InstanceStatus.HEALTHY]
    
    def mark_instance_status(self, service_name: str, instance_id: str, status: InstanceStatus):
        with self._lock:
            if service_name in self._services:
                for instance in self._services[service_name]:
                    if instance.instance_id == instance_id:
                        old_status = instance.status
                        instance.status = status
                        instance.last_check_time = time.time()
                        
                        for listener in self._listeners:
                            listener(service_name, instance, old_status, status)
                        break
    
    def add_status_listener(self, listener: Callable):
        self._listeners.append(listener)
    
    def get_stats(self, service_name: str) -> Dict[str, Any]:
        with self._lock:
            instances = self._services.get(service_name, [])
            
            if not instances:
                return {}
            
            total_requests = sum(i.total_requests for i in instances)
            total_connections = sum(i.connections for i in instances)
            avg_response_time = sum(i.response_time for i in instances) / len(instances)
            
            healthy_count = sum(1 for i in instances if i.status == InstanceStatus.HEALTHY)
            
            return {
                "service_name": service_name,
                "total_instances": len(instances),
                "healthy_instances": healthy_count,
                "total_requests": total_requests,
                "total_connections": total_connections,
                "avg_response_time": avg_response_time
            }


class LoadBalancerMiddleware:
    def __init__(self, load_balancer: LoadBalancer):
        self.load_balancer = load_balancer
    
    def request(self, service_name: str, request_handler: Callable, 
                key: str = None, *args, **kwargs) -> Tuple[bool, Any]:
        instance = self.load_balancer.select_instance(service_name, key)
        
        if not instance:
            return False, None
        
        self.load_balancer.acquire_connection(service_name, instance.instance_id)
        
        try:
            start_time = time.time()
            result = request_handler(instance, *args, **kwargs)
            response_time = time.time() - start_time
            
            self.load_balancer.record_request(
                service_name, instance.instance_id, True, response_time
            )
            
            return True, result
        except Exception as e:
            self.load_balancer.record_request(
                service_name, instance.instance_id, False, 0
            )
            return False, str(e)
        finally:
            self.load_balancer.release_connection(service_name, instance.instance_id)


def main():
    load_balancer = LoadBalancer(RoundRobinStrategy())
    
    print("=== 注册服务实例 ===")
    instances = [
        ServiceInstance("api-1", "192.168.1.1", 8080, weight=3),
        ServiceInstance("api-2", "192.168.1.2", 8080, weight=2),
        ServiceInstance("api-3", "192.168.1.3", 8080, weight=1),
        ServiceInstance("api-4", "192.168.1.4", 8080, weight=1),
    ]
    load_balancer.register_service("api-service", instances)
    
    def on_status_change(service, instance, old_status, new_status):
        print(f"[状态变更] {instance.instance_id}: {old_status.value} -> {new_status.value}")
    
    load_balancer.add_status_listener(on_status_change)
    
    print("\n=== 测试轮询策略 ===")
    load_balancer.set_strategy(RoundRobinStrategy())
    
    distribution = {}
    for i in range(12):
        instance = load_balancer.select_instance("api-service")
        if instance:
            distribution[instance.instance_id] = distribution.get(instance.instance_id, 0) + 1
    
    print("请求分布:", distribution)
    
    print("\n=== 测试加权轮询策略 ===")
    load_balancer.set_strategy(WeightedRoundRobinStrategy())
    
    distribution = {}
    for i in range(21):
        instance = load_balancer.select_instance("api-service")
        if instance:
            distribution[instance.instance_id] = distribution.get(instance.instance_id, 0) + 1
    
    print("请求分布:", distribution)
    print("预期权重: api-1=3, api-2=2, api-3=1, api-4=1")
    
    print("\n=== 测试最少连接策略 ===")
    load_balancer.set_strategy(LeastConnectionsStrategy())
    
    load_balancer.acquire_connection("api-service", "api-1")
    load_balancer.acquire_connection("api-service", "api-1")
    load_balancer.acquire_connection("api-service", "api-2")
    
    for i in range(5):
        instance = load_balancer.select_instance("api-service")
        if instance:
            print(f"选中: {instance.instance_id} (连接数: {instance.connections})")
    
    load_balancer.release_connection("api-service", "api-1")
    load_balancer.release_connection("api-service", "api-1")
    load_balancer.release_connection("api-service", "api-2")
    
    print("\n=== 测试一致性哈希策略 ===")
    load_balancer.set_strategy(ConsistentHashStrategy(virtual_nodes=100))
    
    user_distribution = {}
    for user_id in ["user1", "user2", "user3", "user4", "user5"]:
        instance = load_balancer.select_instance("api-service", user_id)
        if instance:
            user_distribution[user_id] = instance.instance_id
            print(f"{user_id} -> {instance.instance_id}")
    
    print("\n同一用户多次请求:")
    for _ in range(3):
        instance = load_balancer.select_instance("api-service", "user1")
        print(f"user1 -> {instance.instance_id}")
    
    print("\n=== 测试故障转移 ===")
    load_balancer.mark_instance_status("api-service", "api-2", InstanceStatus.UNHEALTHY)
    
    load_balancer.set_strategy(RoundRobinStrategy())
    distribution = {}
    for i in range(9):
        instance = load_balancer.select_instance("api-service")
        if instance:
            distribution[instance.instance_id] = distribution.get(instance.instance_id, 0) + 1
    
    print("故障后请求分布:", distribution)
    
    load_balancer.mark_instance_status("api-service", "api-2", InstanceStatus.HEALTHY)
    
    print("\n=== 测试动态权重调整 ===")
    load_balancer.update_instance_weight("api-service", "api-1", 5)
    load_balancer.update_instance_weight("api-service", "api-3", 3)
    
    load_balancer.set_strategy(WeightedRoundRobinStrategy())
    distribution = {}
    for i in range(18):
        instance = load_balancer.select_instance("api-service")
        if instance:
            distribution[instance.instance_id] = distribution.get(instance.instance_id, 0) + 1
    
    print("调整权重后分布:", distribution)
    
    print("\n=== 测试中间件 ===")
    middleware = LoadBalancerMiddleware(load_balancer)
    
    def mock_handler(instance, *args, **kwargs):
        time.sleep(0.01)
        return f"Response from {instance.address}"
    
    for i in range(3):
        success, result = middleware.request("api-service", mock_handler)
        print(f"请求 {i+1}: {'成功' if success else '失败'} - {result}")
    
    print("\n=== 服务统计 ===")
    stats = load_balancer.get_stats("api-service")
    print(f"总实例数: {stats['total_instances']}")
    print(f"健康实例: {stats['healthy_instances']}")
    print(f"总请求数: {stats['total_requests']}")
    print(f"平均响应时间: {stats['avg_response_time']*1000:.2f}ms")
    
    print("\n=== 实例详情 ===")
    for instance in load_balancer.get_instances("api-service"):
        print(f"{instance.instance_id}:")
        print(f"  地址: {instance.address}")
        print(f"  权重: {instance.weight}")
        print(f"  状态: {instance.status.value}")
        print(f"  请求数: {instance.total_requests}")
        print(f"  成功率: {instance.success_rate*100:.1f}%")


if __name__ == "__main__":
    main()
