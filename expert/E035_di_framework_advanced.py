# -----------------------------
# 题目：实现依赖注入框架高级版。
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
    
    def register_singleton(self, service_type: Type, implementation: Type = None) -> 'Container':
        impl = implementation or service_type
        self._services[service_type] = ServiceDescriptor(
            service_type=service_type,
            implementation_type=impl,
            lifetime=ServiceLifetime.SINGLETON
        )
        return self
    
    def register_scoped(self, service_type: Type, implementation: Type = None) -> 'Container':
        impl = implementation or service_type
        self._services[service_type] = ServiceDescriptor(
            service_type=service_type,
            implementation_type=impl,
            lifetime=ServiceLifetime.SCOPED
        )
        return self
    
    def register_transient(self, service_type: Type, implementation: Type = None) -> 'Container':
        impl = implementation or service_type
        self._services[service_type] = ServiceDescriptor(
            service_type=service_type,
            implementation_type=impl,
            lifetime=ServiceLifetime.TRANSIENT
        )
        return self
    
    def register_factory(self, service_type: Type, factory: Callable, 
                        lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT) -> 'Container':
        self._services[service_type] = ServiceDescriptor(
            service_type=service_type,
            implementation_type=None,
            lifetime=lifetime,
            factory=factory
        )
        return self
    
    def register_instance(self, service_type: Type, instance: Any) -> 'Container':
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

class ServiceCollection:
    def __init__(self):
        self._descriptors: List[ServiceDescriptor] = []
    
    def add_singleton(self, service_type: Type, implementation: Type = None) -> 'ServiceCollection':
        self._descriptors.append(ServiceDescriptor(
            service_type=service_type,
            implementation_type=implementation or service_type,
            lifetime=ServiceLifetime.SINGLETON
        ))
        return self
    
    def add_scoped(self, service_type: Type, implementation: Type = None) -> 'ServiceCollection':
        self._descriptors.append(ServiceDescriptor(
            service_type=service_type,
            implementation_type=implementation or service_type,
            lifetime=ServiceLifetime.SCOPED
        ))
        return self
    
    def add_transient(self, service_type: Type, implementation: Type = None) -> 'ServiceCollection':
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

class Inject:
    def __init__(self, service_type: Type = None):
        self.service_type = service_type
    
    def __set_name__(self, owner, name):
        self.name = name
    
    def __get__(self, obj, owner=None):
        if obj is None:
            return self
        
        if not hasattr(obj, '_container'):
            raise ValueError("对象未关联容器")
        
        service_type = self.service_type or type(getattr(obj, f'_{self.name}', None))
        return obj._container.resolve(service_type)

def injectable(cls):
    original_init = cls.__init__
    
    def __init__(self, *args, container: Container = None, **kwargs):
        if container:
            self._container = container
        original_init(self, *args, **kwargs)
    
    cls.__init__ = __init__
    return cls

def main():
    @injectable
    class ILogger:
        def log(self, message: str):
            print(f"[LOG] {message}")
    
    @injectable
    class ConsoleLogger(ILogger):
        def log(self, message: str):
            print(f"[CONSOLE] {message}")
    
    @injectable
    class IRepository:
        def __init__(self, logger: ILogger):
            self.logger = logger
        
        def save(self, data: str):
            self.logger.log(f"保存: {data}")
    
    @injectable
    class UserService:
        def __init__(self, repository: IRepository, logger: ILogger):
            self.repository = repository
            self.logger = logger
        
        def create_user(self, name: str):
            self.logger.log(f"创建用户: {name}")
            self.repository.save(name)
    
    print("=== 配置服务 ===")
    services = (ServiceCollection()
                .add_singleton(ILogger, ConsoleLogger)
                .add_transient(IRepository)
                .add_transient(UserService))
    
    container = services.build()
    
    print("\n=== 解析服务 ===")
    service1 = container.resolve(UserService)
    service2 = container.resolve(UserService)
    
    print(f"UserService是瞬态: {service1 is not service2}")
    
    print("\n=== 使用服务 ===")
    service1.create_user("张三")
    
    print("\n=== 使用Scope ===")
    scope = container.create_scope()
    
    repo1 = scope.resolve(IRepository)
    repo2 = scope.resolve(IRepository)
    
    print(f"Scope内IRepository是同一个: {repo1 is repo2}")


if __name__ == "__main__":
    main()
