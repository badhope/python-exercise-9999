# -----------------------------
# 题目：实现简单的依赖注入容器。
# -----------------------------

from typing import Dict, Type, Any, Callable
from enum import Enum

class ServiceLifetime(Enum):
    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"

class ServiceDescriptor:
    def __init__(self, service_type: Type, implementation, lifetime: ServiceLifetime):
        self.service_type = service_type
        self.implementation = implementation
        self.lifetime = lifetime
        self.instance = None

class Container:
    def __init__(self):
        self._services: Dict[Type, ServiceDescriptor] = {}
        self._singletons: Dict[Type, Any] = {}
    
    def register_singleton(self, service_type: Type, implementation=None):
        impl = implementation or service_type
        self._services[service_type] = ServiceDescriptor(
            service_type, impl, ServiceLifetime.SINGLETON
        )
        return self
    
    def register_transient(self, service_type: Type, implementation=None):
        impl = implementation or service_type
        self._services[service_type] = ServiceDescriptor(
            service_type, impl, ServiceLifetime.TRANSIENT
        )
        return self
    
    def register_instance(self, service_type: Type, instance):
        self._singletons[service_type] = instance
        self._services[service_type] = ServiceDescriptor(
            service_type, type(instance), ServiceLifetime.SINGLETON
        )
        return self
    
    def register_factory(self, service_type: Type, factory: Callable, lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT):
        descriptor = ServiceDescriptor(service_type, factory, lifetime)
        descriptor.is_factory = True
        self._services[service_type] = descriptor
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
        
        return self._create_instance(descriptor)
    
    def _create_instance(self, descriptor: ServiceDescriptor) -> Any:
        if hasattr(descriptor, 'is_factory') and descriptor.is_factory:
            return descriptor.implementation(self)
        
        implementation = descriptor.implementation
        
        import inspect
        sig = inspect.signature(implementation.__init__)
        params = {}
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            param_type = param.annotation
            if param_type != inspect.Parameter.empty and param_type in self._services:
                params[param_name] = self.resolve(param_type)
        
        return implementation(**params)
    
    def is_registered(self, service_type: Type) -> bool:
        return service_type in self._services

class ServiceProvider:
    def __init__(self, container: Container):
        self.container = container
    
    def get_service(self, service_type: Type) -> Any:
        return self.container.resolve(service_type)
    
    def get_required_service(self, service_type: Type) -> Any:
        if not self.container.is_registered(service_type):
            raise ValueError(f"服务 {service_type.__name__} 未注册")
        return self.get_service(service_type)

class DatabaseService:
    def __init__(self):
        self.connection_string = "sqlite:///:memory:"
    
    def query(self, sql):
        return f"执行查询: {sql}"

class LoggerService:
    def __init__(self, db: DatabaseService):
        self.db = db
    
    def log(self, message):
        self.db.query(f"INSERT INTO logs VALUES ('{message}')")
        print(f"日志: {message}")

class UserService:
    def __init__(self, db: DatabaseService, logger: LoggerService):
        self.db = db
        self.logger = logger
    
    def get_user(self, user_id):
        self.logger.log(f"获取用户 {user_id}")
        return self.db.query(f"SELECT * FROM users WHERE id = {user_id}")

def main():
    container = Container()
    
    container.register_singleton(DatabaseService)
    container.register_singleton(LoggerService)
    container.register_transient(UserService)
    
    container.register_instance(str, "应用配置")
    
    print("=== 解析服务 ===")
    db1 = container.resolve(DatabaseService)
    db2 = container.resolve(DatabaseService)
    print(f"DatabaseService是单例: {db1 is db2}")
    
    user_service1 = container.resolve(UserService)
    user_service2 = container.resolve(UserService)
    print(f"UserService是瞬态: {user_service1 is not user_service2}")
    
    print("\n=== 使用服务 ===")
    user_service1.get_user(1)


if __name__ == "__main__":
    main()
