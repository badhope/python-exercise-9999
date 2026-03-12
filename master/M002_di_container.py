# -----------------------------
# 题目：实现简单的依赖注入容器。
# 描述：支持自动依赖解析和生命周期管理。
# -----------------------------

class Container:
    def __init__(self):
        self._bindings = {}
        self._instances = {}
        self._resolving = set()
    
    def bind(self, abstract, concrete, singleton=False):
        self._bindings[abstract] = {
            'concrete': concrete,
            'singleton': singleton
        }
    
    def singleton(self, abstract, concrete):
        self.bind(abstract, concrete, True)
    
    def instance(self, abstract, instance):
        self._instances[abstract] = instance
    
    def make(self, abstract):
        if abstract in self._instances:
            return self._instances[abstract]
        
        if abstract not in self._bindings:
            raise ValueError(f"未绑定: {abstract}")
        
        binding = self._bindings[abstract]
        
        if abstract in self._resolving:
            raise ValueError(f"循环依赖: {abstract}")
        
        self._resolving.add(abstract)
        
        try:
            instance = self._build(binding['concrete'])
        finally:
            self._resolving.remove(abstract)
        
        if binding['singleton']:
            self._instances[abstract] = instance
        
        return instance
    
    def _build(self, concrete):
        if callable(concrete):
            return concrete(self)
        return concrete

class ServiceA:
    def __init__(self):
        self.name = "ServiceA"

class ServiceB:
    def __init__(self, container):
        self.service_a = container.make(ServiceA)
        self.name = "ServiceB"

def main():
    container = Container()
    container.singleton(ServiceA, lambda c: ServiceA())
    container.bind(ServiceB, lambda c: ServiceB(c))
    
    b1 = container.make(ServiceB)
    b2 = container.make(ServiceB)
    
    print(f"ServiceB: {b1.name}, 依赖: {b1.service_a.name}")
    print(f"ServiceA是单例: {b1.service_a is b2.service_a}")


if __name__ == "__main__":
    main()
