# -----------------------------
# 题目：实现简单的依赖注入容器扩展版。
# -----------------------------

from typing import Dict, Type, Any, Callable, List, Optional, get_type_hints
from dataclasses import dataclass
from enum import Enum
import inspect

class ServiceLifetime(Enum):
    SINGLETON = "singleton"
    SCOPED = "scoped"
    TRANSIENT = "transient"

@dataclass
class ServiceDescriptor:
    service_type: Type
    implementation_type: Type
    lifetime: ServiceLifetime
    factory: Callable = None
    instance: Any = None

class Container:
    def __init__(self):
        self._services: Dict[Type, ServiceDescriptor] = {}
        self._singletons: Dict[Type, Any] = {}
        self._scoped_instances: Dict[Type, Any] = {}
    
    def register_singleton(self, service_type: Type, implementation: Type = None):
        impl = implementation or service_type
        self._services[service_type] = ServiceDescriptor(
            service_type=service_type,
            implementation_type=impl,
            lifetime=ServiceLifetime.SINGLETON
        )
        return self
    
    def register_scoped(self, service_type: Type, implementation: Type = None):
        impl = implementation or service_type
        self._services[service_type] = ServiceDescriptor(
            service_type=service_type,
            implementation_type=impl,
            lifetime=ServiceLifetime.SCOPED
        )
        return self
    
    def register_transient(self, service_type: Type, implementation: Type = None):
        impl = implementation or service_type
        self._services[service_type] = ServiceDescriptor(
            service_type=service_type,
            implementation_type=impl,
            lifetime=ServiceLifetime.TRANSIENT
        )
        return self
    
    def register_factory(self, service_type: Type, factory: Callable, lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT):
        self._services[service_type] = ServiceDescriptor(
            service_type=service_type,
            implementation_type=None,
            lifetime=lifetime,
            factory=factory
        )
        return self
    
    def register_instance(self, service_type: Type, instance: Any):
        self._services[service_type] = ServiceDescriptor(
            service_type=service_type,
            implementation_type=type(instance),
            lifetime=ServiceLifetime.SINGLETON,
            instance=instance
        )
        self._singletons[service_type] = instance
        return self
    
    def resolve(self, service_type: Type) -> Any:
        if service_type not in self._services:
            raise ValueError(f"服务 {service_type.__name__} 未注册")
        
        descriptor = self._services[service_type]
        
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
        if descriptor.factory:
            return descriptor.factory(self)
        
        impl = descriptor.implementation_type
        dependencies = self._get_dependencies(impl)
        
        return impl(**dependencies)
    
    def _get_dependencies(self, impl: Type) -> Dict[str, Any]:
        dependencies = {}
        
        if impl.__init__ == object.__init__:
            return dependencies
        
        sig = inspect.signature(impl.__init__)
        hints = get_type_hints(impl.__init__)
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            param_type = hints.get(param_name)
            if param_type and param_type in self._services:
                dependencies[param_name] = self.resolve(param_type)
            elif param.default != inspect.Parameter.empty:
                dependencies[param_name] = param.default
        
        return dependencies
    
    def create_scope(self) -> 'Scope':
        return Scope(self)
    
    def is_registered(self, service_type: Type) -> bool:
        return service_type in self._services

class Scope:
    def __init__(self, container: Container):
        self.container = container
        self._instances: Dict[Type, Any] = {}
    
    def resolve(self, service_type: Type) -> Any:
        descriptor = self.container._services.get(service_type)
        
        if not descriptor:
            raise ValueError(f"服务 {service_type.__name__} 未注册")
        
        if descriptor.lifetime == ServiceLifetime.SCOPED:
            if service_type in self._instances:
                return self._instances[service_type]
            
            instance = self.container._create_instance(descriptor)
            self._instances[service_type] = instance
            return instance
        
        return self.container.resolve(service_type)
    
    def dispose(self):
        self._instances.clear()

class ServiceProvider:
    def __init__(self, container: Container):
        self.container = container
    
    def get_service(self, service_type: Type) -> Optional[Any]:
        if self.container.is_registered(service_type):
            return self.container.resolve(service_type)
        return None
    
    def get_required_service(self, service_type: Type) -> Any:
        return self.container.resolve(service_type)
    
    def get_services(self, service_type: Type) -> List[Any]:
        return [self.get_service(service_type)]

class ServiceCollection:
    def __init__(self):
        self._descriptors: List[ServiceDescriptor] = []
    
    def add_singleton(self, service_type: Type, implementation: Type = None):
        self._descriptors.append(ServiceDescriptor(
            service_type=service_type,
            implementation_type=implementation or service_type,
            lifetime=ServiceLifetime.SINGLETON
        ))
        return self
    
    def add_scoped(self, service_type: Type, implementation: Type = None):
        self._descriptors.append(ServiceDescriptor(
            service_type=service_type,
            implementation_type=implementation or service_type,
            lifetime=ServiceLifetime.SCOPED
        ))
        return self
    
    def add_transient(self, service_type: Type, implementation: Type = None):
        self._descriptors.append(ServiceDescriptor(
            service_type=service_type,
            implementation_type=implementation or service_type,
            lifetime=ServiceLifetime.TRANSIENT
        ))
        return self
    
    def build(self) -> Container:
        container = Container()
        for desc in self._descriptors:
            container._services[desc.service_type] = desc
        return container

def main():
    class IRepository:
        def get(self, id: int):
            pass
    
    class Repository(IRepository):
        def get(self, id: int):
            return f"数据{id}"
    
    class Service:
        def __init__(self, repository: IRepository):
            self.repository = repository
        
        def process(self, id: int):
            return self.repository.get(id)
    
    services = ServiceCollection()
    services.add_singleton(IRepository, Repository)
    services.add_transient(Service)
    
    container = services.build()
    
    print("=== 解析服务 ===")
    service1 = container.resolve(Service)
    service2 = container.resolve(Service)
    
    print(f"Service是瞬态: {service1 is not service2}")
    print(f"Repository是单例: {service1.repository is service2.repository}")
    
    print(f"\n处理结果: {service1.process(1)}")
    
    print("\n=== 使用Scope ===")
    scope1 = container.create_scope()
    scope2 = container.create_scope()
    
    print(f"Scope已创建")


if __name__ == "__main__":
    main()
