# -----------------------------
# 题目：实现依赖注入容器。
# -----------------------------

import inspect

class Container:
    def __init__(self):
        self.services = {}
        self.singleton = {}
    
    def register(self, name, factory, singleton=False):
        self.services[name] = {"factory": factory, "singleton": singleton}
    
    def register_instance(self, name, instance):
        self.singleton[name] = instance
    
    def resolve(self, name):
        if name in self.singleton:
            return self.singleton[name]
        
        if name not in self.services:
            raise ValueError(f"Service {name} not registered")
        
        service = self.services[name]
        factory = service["factory"]
        
        sig = inspect.signature(factory)
        deps = {}
        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue
            if param.annotation != inspect.Parameter.empty:
                dep_name = param.annotation.__name__ if inspect.isclass(param.annotation) else str(param.annotation)
                deps[param_name] = self.resolve(dep_name)
        
        instance = factory(**deps)
        
        if service["singleton"]:
            self.singleton[name] = instance
        
        return instance

class ServiceA:
    def __init__(self):
        self.value = "A"

class ServiceB:
    def __init__(self, service_a: ServiceA):
        self.service_a = service_a

class ServiceC:
    def __init__(self, service_b: ServiceB):
        self.service_b = service_b

if __name__ == "__main__":
    container = Container()
    container.register("ServiceA", lambda: ServiceA(), singleton=True)
    container.register("ServiceB", lambda service_a: ServiceB(service_a), singleton=True)
    container.register("ServiceC", lambda service_b: ServiceC(service_b))
    
    c1 = container.resolve("ServiceC")
    c2 = container.resolve("ServiceC")
    print(f"Same instance: {c1 is c2}")
    print(f"ServiceA same: {c1.service_b.service_a is c2.service_b.service_a}")
