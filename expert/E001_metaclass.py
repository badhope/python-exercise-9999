# -----------------------------
# 题目：实现简单的元类。
# 描述：使用元类自动注册类。
# -----------------------------

class RegistryMeta(type):
    registry = {}
    
    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        if name != "BaseModel":
            mcs.registry[name] = cls
        return cls

class BaseModel(metaclass=RegistryMeta):
    pass

class User(BaseModel):
    def __init__(self, name):
        self.name = name

class Product(BaseModel):
    def __init__(self, title):
        self.title = title

def main():
    print(f"已注册的类: {list(RegistryMeta.registry.keys())}")
    user = RegistryMeta.registry["User"]("张三")
    print(f"创建用户: {user.name}")


if __name__ == "__main__":
    main()
