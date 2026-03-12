# -----------------------------
# 题目：实现依赖注入容器。
# 描述：支持服务注册、生命周期管理、依赖解析。
# -----------------------------

from abc import ABC, abstractmethod
from typing import Dict, Any, Type, Callable, Optional, List, get_type_hints
from dataclasses import dataclass
from enum import Enum
import inspect

class ServiceLifetime(Enum):
    TRANSIENT = "transient"
    SINGLETON = "singleton"
    SCOPED = "scoped"

@dataclass
class ServiceDescriptor:
    service_type: Type
    implementation_type: Optional[Type] = None
    factory: Optional[Callable] = None
    instance: Optional[Any] = None
    lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT

class DIContainer:
    def __init__(self):
        self._services: Dict[Type, ServiceDescriptor] = {}
        self._singletons: Dict[Type, Any] = {}
        self._scoped_instances: Dict[Type, Any] = {}
        self._parent: Optional['DIContainer'] = None
    
    def register(
        self,
        service_type: Type,
        implementation_type: Type = None,
        factory: Callable = None,
        lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT
    ) -> 'DIContainer':
        descriptor = ServiceDescriptor(
            service_type=service_type,
            implementation_type=implementation_type or service_type,
            factory=factory,
            lifetime=lifetime
        )
        self._services[service_type] = descriptor
        return self
    
    def register_singleton(self, service_type: Type, implementation_type: Type = None) -> 'DIContainer':
        return self.register(service_type, implementation_type, lifetime=ServiceLifetime.SINGLETON)
    
    def register_transient(self, service_type: Type, implementation_type: Type = None) -> 'DIContainer':
        return self.register(service_type, implementation_type, lifetime=ServiceLifetime.TRANSIENT)
    
    def register_factory(
        self,
        service_type: Type,
        factory: Callable,
        lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT
    ) -> 'DIContainer':
        return self.register(service_type, factory=factory, lifetime=lifetime)
    
    def register_instance(self, service_type: Type, instance: Any) -> 'DIContainer':
        descriptor = ServiceDescriptor(
            service_type=service_type,
            instance=instance,
            lifetime=ServiceLifetime.SINGLETON
        )
        self._services[service_type] = descriptor
        self._singletons[service_type] = instance
        return self
    
    def resolve(self, service_type: Type) -> Any:
        descriptor = self._services.get(service_type)
        if not descriptor:
            raise ValueError(f"服务未注册: {service_type}")
        
        if descriptor.lifetime == ServiceLifetime.SINGLETON:
            if service_type in self._singletons:
                return self._singletons[service_type]
            
            instance = self._create_instance(descriptor)
            self._singletons[service_type] = instance
            return instance
        
        if descriptor.lifetime == ServiceLifetime.SCOPED:
            if service_type in self._scoped_instances:
                return self._scoped_instances[service_type]
            
            instance = self._create_instance(descriptor)
            self._scoped_instances[service_type] = instance
            return instance
        
        return self._create_instance(descriptor)
    
    def _create_instance(self, descriptor: ServiceDescriptor) -> Any:
        if descriptor.instance is not None:
            return descriptor.instance
        
        if descriptor.factory:
            return descriptor.factory(self)
        
        implementation_type = descriptor.implementation_type
        if not implementation_type:
            raise ValueError(f"无法创建实例: {descriptor.service_type}")
        
        dependencies = self._resolve_dependencies(implementation_type)
        
        return implementation_type(**dependencies)
    
    def _resolve_dependencies(self, cls: Type) -> Dict[str, Any]:
        dependencies = {}
        
        try:
            hints = get_type_hints(cls.__init__)
        except:
            hints = {}
        
        sig = inspect.signature(cls.__init__)
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            param_type = hints.get(param_name)
            
            if param_type and param_type in self._services:
                dependencies[param_name] = self.resolve(param_type)
            elif param.default is not inspect.Parameter.empty:
                continue
            else:
                dependencies[param_name] = None
        
        return dependencies
    
    def create_scope(self) -> 'DIContainer':
        scoped = DIContainer()
        scoped._services = self._services.copy()
        scoped._singletons = self._singletons.copy()
        scoped._parent = self
        return scoped
    
    def is_registered(self, service_type: Type) -> bool:
        return service_type in self._services
    
    def get_registered_services(self) -> List[Type]:
        return list(self._services.keys())

class IServiceA(ABC):
    @abstractmethod
    def do_something(self) -> str:
        pass

class ServiceA(IServiceA):
    def __init__(self):
        self.name = "ServiceA"
    
    def do_something(self) -> str:
        return f"{self.name} 执行操作"

class IServiceB(ABC):
    @abstractmethod
    def do_another(self) -> str:
        pass

class ServiceB(IServiceB):
    def __init__(self, service_a: IServiceA):
        self.service_a = service_a
    
    def do_another(self) -> str:
        return f"ServiceB 使用 {self.service_a.do_something()}"

class ILogger(ABC):
    @abstractmethod
    def log(self, message: str):
        pass

class ConsoleLogger(ILogger):
    def __init__(self, prefix: str = "[LOG]"):
        self.prefix = prefix
    
    def log(self, message: str):
        print(f"{self.prefix} {message}")

def main():
    container = DIContainer()
    
    container.register_singleton(IServiceA, ServiceA)
    container.register_transient(IServiceB, ServiceB)
    container.register_factory(
        ILogger,
        lambda c: ConsoleLogger("[APP]"),
        lifetime=ServiceLifetime.SINGLETON
    )
    
    service_a1 = container.resolve(IServiceA)
    service_a2 = container.resolve(IServiceA)
    print(f"单例服务相同: {service_a1 is service_a2}")
    
    service_b1 = container.resolve(IServiceB)
    service_b2 = container.resolve(IServiceB)
    print(f"瞬态服务不同: {service_b1 is not service_b2}")
    
    print(f"\n{service_b1.do_another()}")
    
    logger = container.resolve(ILogger)
    logger.log("测试日志")
    
    print(f"\n已注册服务: {[s.__name__ for s in container.get_registered_services()]}")

if __name__ == "__main__":
    main()
