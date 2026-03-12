# -----------------------------
# 题目：实现元编程高级版。
# -----------------------------

from typing import Any, Dict, List, Type, Callable
import inspect

class MetaClass(type):
    def __new__(mcs, name: str, bases: tuple, namespace: dict):
        cls = super().__new__(mcs, name, bases, namespace)
        
        methods = {}
        for key, value in namespace.items():
            if callable(value) and not key.startswith('_'):
                methods[key] = value
        
        cls._methods = methods
        cls._class_name = name
        
        return cls
    
    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)
        if hasattr(cls, '_post_init'):
            cls._post_init(instance)
        return instance

class TracingMeta(type):
    def __new__(mcs, name: str, bases: tuple, namespace: dict):
        for key, value in namespace.items():
            if callable(value) and not key.startswith('_'):
                namespace[key] = mcs._trace(value)
        
        return super().__new__(mcs, name, bases, namespace)
    
    @staticmethod
    def _trace(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            print(f"调用: {func.__name__}")
            result = func(*args, **kwargs)
            print(f"返回: {func.__name__} -> {result}")
            return result
        return wrapper

class SingletonMeta(type):
    _instances: Dict[type, Any] = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class RegisteredMeta(type):
    _registry: Dict[str, type] = {}
    
    def __new__(mcs, name: str, bases: tuple, namespace: dict):
        cls = super().__new__(mcs, name, bases, namespace)
        if name != 'Base':
            mcs._registry[name] = cls
        return cls
    
    @classmethod
    def get_class(mcs, name: str) -> type:
        return mcs._registry.get(name)
    
    @classmethod
    def create_instance(mcs, name: str, *args, **kwargs) -> Any:
        cls = mcs.get_class(name)
        if cls:
            return cls(*args, **kwargs)
        return None

class ValidatedMeta(type):
    def __new__(mcs, name: str, bases: tuple, namespace: dict):
        annotations = namespace.get('__annotations__', {})
        
        for attr_name, attr_type in annotations.items():
            namespace[f'_validate_{attr_name}'] = mcs._create_validator(attr_name, attr_type)
        
        cls = super().__new__(mcs, name, bases, namespace)
        return cls
    
    @staticmethod
    def _create_validator(name: str, expected_type: type) -> Callable:
        def validator(self, value):
            if not isinstance(value, expected_type):
                raise TypeError(f"{name} 必须是 {expected_type.__name__} 类型")
            return value
        return validator

class AttributeAccessor:
    def __getattr__(self, name: str) -> Any:
        if name.startswith('get_'):
            attr_name = name[4:]
            return lambda: getattr(self, f'_{attr_name}', None)
        
        if name.startswith('set_'):
            attr_name = name[4:]
            def setter(value):
                setattr(self, f'_{attr_name}', value)
            return setter
        
        raise AttributeError(f"'{type(self).__name__}' 对象没有属性 '{name}'")

class DynamicClass:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __getattr__(self, name: str) -> Any:
        if name in self.__dict__:
            return self.__dict__[name]
        return None
    
    def __setattr__(self, name: str, value: Any):
        validator = getattr(self.__class__, f'_validate_{name}', None)
        if validator:
            value = validator(self, value)
        super().__setattr__(name, value)

def create_class(name: str, attributes: Dict[str, Any] = None, methods: Dict[str, Callable] = None) -> type:
    namespace = attributes or {}
    namespace.update(methods or {})
    return type(name, (), namespace)

def add_method(cls: type, name: str, func: Callable):
    setattr(cls, name, func)

def add_property(cls: type, name: str, getter: Callable = None, setter: Callable = None):
    prop = property(getter, setter)
    setattr(cls, name, prop)

class Model(metaclass=MetaClass):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @classmethod
    def _post_init(cls, instance):
        instance._initialized = True
    
    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

class TracedModel(metaclass=TracingMeta):
    def __init__(self, value):
        self.value = value
    
    def double(self):
        return self.value * 2
    
    def triple(self):
        return self.value * 3

class Plugin(metaclass=RegisteredMeta):
    pass

class AudioPlugin(Plugin):
    def process(self):
        return "处理音频"

class VideoPlugin(Plugin):
    def process(self):
        return "处理视频"

def main():
    print("=== MetaClass ===")
    user = Model(name="张三", age=25)
    print(f"用户: {user.to_dict()}")
    print(f"类方法: {Model._methods}")
    
    print("\n=== TracingMeta ===")
    model = TracedModel(10)
    print(f"结果: {model.double()}")
    
    print("\n=== RegisteredMeta ===")
    print(f"注册的类: {list(RegisteredMeta._registry.keys())}")
    
    audio = RegisteredMeta.create_instance('AudioPlugin')
    print(f"音频插件: {audio.process()}")
    
    video = RegisteredMeta.create_instance('VideoPlugin')
    print(f"视频插件: {video.process()}")
    
    print("\n=== 动态创建类 ===")
    Person = create_class(
        'Person',
        {'species': 'human'},
        {'greet': lambda self: f"Hello, I'm {self.name}"}
    )
    
    p = Person()
    p.name = "李四"
    print(f"物种: {p.species}")
    print(f"问候: {p.greet()}")
    
    print("\n=== 添加方法 ===")
    def get_age(self):
        return self._age
    
    def set_age(self, value):
        self._age = value
    
    add_property(Person, 'age', get_age, set_age)
    
    p.age = 30
    print(f"年龄: {p.age}")


if __name__ == "__main__":
    main()
