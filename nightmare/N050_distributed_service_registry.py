"""
N050 - 分布式服务注册中心
难度：Nightmare

题目描述：
实现一个分布式服务注册中心，支持服务的注册、发现、健康检查和故障转移。
系统需要处理服务实例的生命周期管理、服务元数据存储、服务变更通知等核心功能。

学习目标：
1. 理解服务注册中心的核心概念和架构
2. 掌握服务实例的生命周期管理
3. 实现服务的健康检查机制
4. 处理服务变更的通知和订阅

输入输出要求：
输入：服务操作请求（注册、注销、查询、订阅）
输出：操作结果和服务实例列表

预期解决方案：
使用观察者模式实现服务变更通知，使用心跳机制实现健康检查。
"""

import json
import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set


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
    metadata: Dict[str, Any] = field(default_factory=dict)
    registration_time: float = field(default_factory=time.time)
    last_heartbeat: float = field(default_factory=time.time)
    lease_duration: float = 30.0
    
    @property
    def address(self) -> str:
        return f"{self.host}:{self.port}"
    
    @property
    def is_expired(self) -> bool:
        return time.time() - self.last_heartbeat > self.lease_duration
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "instance_id": self.instance_id,
            "service_name": self.service_name,
            "host": self.host,
            "port": self.port,
            "status": self.status.value,
            "metadata": self.metadata,
            "registration_time": self.registration_time,
            "last_heartbeat": self.last_heartbeat
        }


@dataclass
class ServiceMetadata:
    service_name: str
    instances: Dict[str, ServiceInstance] = field(default_factory=dict)
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)


class ServiceRegistryEvent:
    REGISTER = "register"
    DEREGISTER = "deregister"
    HEARTBEAT = "heartbeat"
    STATUS_CHANGE = "status_change"
    EXPIRED = "expired"


@dataclass
class RegistryEvent:
    event_type: str
    service_name: str
    instance: ServiceInstance
    timestamp: float = field(default_factory=time.time)


class ServiceRegistry:
    def __init__(self, heartbeat_interval: float = 10.0, lease_duration: float = 30.0):
        self.heartbeat_interval = heartbeat_interval
        self.lease_duration = lease_duration
        self._services: Dict[str, ServiceMetadata] = {}
        self._instance_index: Dict[str, ServiceInstance] = {}
        self._listeners: List[Callable[[RegistryEvent], None]] = []
        self._lock = threading.RLock()
        self._running = False
        self._eviction_thread: Optional[threading.Thread] = None
    
    def register(self, service_name: str, host: str, port: int,
                 metadata: Dict[str, Any] = None) -> ServiceInstance:
        with self._lock:
            instance_id = f"{service_name}-{uuid.uuid4().hex[:8]}"
            
            instance = ServiceInstance(
                instance_id=instance_id,
                service_name=service_name,
                host=host,
                port=port,
                metadata=metadata or {},
                lease_duration=self.lease_duration
            )
            
            if service_name not in self._services:
                self._services[service_name] = ServiceMetadata(service_name=service_name)
            
            self._services[service_name].instances[instance_id] = instance
            self._services[service_name].updated_at = time.time()
            self._instance_index[instance_id] = instance
        
        self._notify_listeners(RegistryEvent(
            event_type=ServiceRegistryEvent.REGISTER,
            service_name=service_name,
            instance=instance
        ))
        
        return instance
    
    def deregister(self, instance_id: str) -> bool:
        with self._lock:
            instance = self._instance_index.get(instance_id)
            if not instance:
                return False
            
            service_name = instance.service_name
            if service_name in self._services:
                if instance_id in self._services[service_name].instances:
                    del self._services[service_name].instances[instance_id]
                    self._services[service_name].updated_at = time.time()
            
            del self._instance_index[instance_id]
        
        self._notify_listeners(RegistryEvent(
            event_type=ServiceRegistryEvent.DEREGISTER,
            service_name=service_name,
            instance=instance
        ))
        
        return True
    
    def heartbeat(self, instance_id: str) -> bool:
        with self._lock:
            instance = self._instance_index.get(instance_id)
            if not instance:
                return False
            
            instance.last_heartbeat = time.time()
            
            if instance.status == ServiceStatus.DOWN:
                instance.status = ServiceStatus.UP
                self._notify_listeners(RegistryEvent(
                    event_type=ServiceRegistryEvent.STATUS_CHANGE,
                    service_name=instance.service_name,
                    instance=instance
                ))
        
        return True
    
    def get_instance(self, instance_id: str) -> Optional[ServiceInstance]:
        with self._lock:
            return self._instance_index.get(instance_id)
    
    def get_instances(self, service_name: str) -> List[ServiceInstance]:
        with self._lock:
            if service_name not in self._services:
                return []
            return list(self._services[service_name].instances.values())
    
    def get_healthy_instances(self, service_name: str) -> List[ServiceInstance]:
        with self._lock:
            if service_name not in self._services:
                return []
            return [
                inst for inst in self._services[service_name].instances.values()
                if inst.status == ServiceStatus.UP and not inst.is_expired
            ]
    
    def get_all_services(self) -> List[str]:
        with self._lock:
            return list(self._services.keys())
    
    def set_instance_status(self, instance_id: str, status: ServiceStatus) -> bool:
        with self._lock:
            instance = self._instance_index.get(instance_id)
            if not instance:
                return False
            
            instance.status = status
        
        self._notify_listeners(RegistryEvent(
            event_type=ServiceRegistryEvent.STATUS_CHANGE,
            service_name=instance.service_name,
            instance=instance
        ))
        
        return True
    
    def add_listener(self, listener: Callable[[RegistryEvent], None]):
        self._listeners.append(listener)
    
    def remove_listener(self, listener: Callable[[RegistryEvent], None]):
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    def _notify_listeners(self, event: RegistryEvent):
        for listener in self._listeners:
            try:
                listener(event)
            except Exception:
                pass
    
    def start_eviction(self):
        with self._lock:
            if self._running:
                return
            self._running = True
        
        self._eviction_thread = threading.Thread(target=self._eviction_loop, daemon=True)
        self._eviction_thread.start()
    
    def stop_eviction(self):
        with self._lock:
            self._running = False
        
        if self._eviction_thread:
            self._eviction_thread.join(timeout=5)
    
    def _eviction_loop(self):
        while self._running:
            self._evict_expired_instances()
            time.sleep(self.heartbeat_interval)
    
    def _evict_expired_instances(self):
        expired = []
        
        with self._lock:
            for instance_id, instance in list(self._instance_index.items()):
                if instance.is_expired:
                    expired.append(instance)
        
        for instance in expired:
            self.set_instance_status(instance.instance_id, ServiceStatus.DOWN)
            self._notify_listeners(RegistryEvent(
                event_type=ServiceRegistryEvent.EXPIRED,
                service_name=instance.service_name,
                instance=instance
            ))


class ServiceDiscovery:
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        self._cache: Dict[str, List[ServiceInstance]] = {}
        self._cache_time: Dict[str, float] = {}
        self._cache_ttl: float = 5.0
        self._lock = threading.Lock()
    
    def discover(self, service_name: str, use_cache: bool = True) -> List[ServiceInstance]:
        if use_cache:
            with self._lock:
                if service_name in self._cache:
                    if time.time() - self._cache_time.get(service_name, 0) < self._cache_ttl:
                        return self._cache[service_name]
        
        instances = self.registry.get_healthy_instances(service_name)
        
        with self._lock:
            self._cache[service_name] = instances
            self._cache_time[service_name] = time.time()
        
        return instances
    
    def get_one_instance(self, service_name: str) -> Optional[ServiceInstance]:
        instances = self.discover(service_name)
        if not instances:
            return None
        return instances[0]
    
    def invalidate_cache(self, service_name: str = None):
        with self._lock:
            if service_name:
                self._cache.pop(service_name, None)
                self._cache_time.pop(service_name, None)
            else:
                self._cache.clear()
                self._cache_time.clear()


class ServiceClient:
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        self.discovery = ServiceDiscovery(registry)
        self._instance_id: Optional[str] = None
        self._heartbeat_thread: Optional[threading.Thread] = None
        self._running = False
    
    def register_self(self, service_name: str, host: str, port: int,
                      metadata: Dict[str, Any] = None) -> ServiceInstance:
        instance = self.registry.register(service_name, host, port, metadata)
        self._instance_id = instance.instance_id
        return instance
    
    def start_heartbeat(self, interval: float = 10.0):
        if self._running:
            return
        
        self._running = True
        self._heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop,
            args=(interval,),
            daemon=True
        )
        self._heartbeat_thread.start()
    
    def stop_heartbeat(self):
        self._running = False
        if self._heartbeat_thread:
            self._heartbeat_thread.join(timeout=5)
    
    def _heartbeat_loop(self, interval: float):
        while self._running:
            if self._instance_id:
                self.registry.heartbeat(self._instance_id)
            time.sleep(interval)
    
    def deregister_self(self):
        if self._instance_id:
            self.registry.deregister(self._instance_id)
            self._instance_id = None


def main():
    registry = ServiceRegistry(heartbeat_interval=5.0, lease_duration=15.0)
    
    events_received = []
    
    def on_registry_event(event: RegistryEvent):
        events_received.append(event)
        print(f"[事件] {event.event_type}: {event.instance.instance_id}")
    
    registry.add_listener(on_registry_event)
    
    print("=== 服务注册 ===")
    instance1 = registry.register("user-service", "192.168.1.1", 8080, {"version": "1.0"})
    print(f"注册实例: {instance1.instance_id} @ {instance1.address}")
    
    instance2 = registry.register("user-service", "192.168.1.2", 8080, {"version": "1.0"})
    print(f"注册实例: {instance2.instance_id} @ {instance2.address}")
    
    instance3 = registry.register("order-service", "192.168.1.3", 8081, {"version": "2.0"})
    print(f"注册实例: {instance3.instance_id} @ {instance3.address}")
    
    print("\n=== 服务发现 ===")
    discovery = ServiceDiscovery(registry)
    
    user_instances = discovery.discover("user-service")
    print(f"user-service 实例数: {len(user_instances)}")
    for inst in user_instances:
        print(f"  - {inst.address} ({inst.status.value})")
    
    order_instances = discovery.discover("order-service")
    print(f"order-service 实例数: {len(order_instances)}")
    
    print("\n=== 服务心跳 ===")
    registry.heartbeat(instance1.instance_id)
    print(f"发送心跳: {instance1.instance_id}")
    
    print("\n=== 服务状态变更 ===")
    registry.set_instance_status(instance2.instance_id, ServiceStatus.OUT_OF_SERVICE)
    print(f"设置状态: {instance2.instance_id} -> OUT_OF_SERVICE")
    
    healthy = registry.get_healthy_instances("user-service")
    print(f"健康实例数: {len(healthy)}")
    
    print("\n=== 服务注销 ===")
    registry.deregister(instance3.instance_id)
    print(f"注销实例: {instance3.instance_id}")
    
    all_services = registry.get_all_services()
    print(f"所有服务: {all_services}")
    
    print("\n=== 服务客户端 ===")
    client = ServiceClient(registry)
    
    my_instance = client.register_self("payment-service", "192.168.1.4", 8082)
    print(f"客户端注册: {my_instance.instance_id}")
    
    client.start_heartbeat(interval=2.0)
    print("开始心跳...")
    time.sleep(3)
    
    client.stop_heartbeat()
    client.deregister_self()
    print("客户端注销")
    
    print("\n=== 事件统计 ===")
    print(f"总共收到 {len(events_received)} 个事件")
    event_types = {}
    for event in events_received:
        event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
    for event_type, count in event_types.items():
        print(f"  {event_type}: {count}")


if __name__ == "__main__":
    main()