# -----------------------------
# 题目：实现序列化框架高级版。
# -----------------------------

from typing import Any, Dict, Type, Callable, List, Optional, get_type_hints
from dataclasses import dataclass, is_dataclass
from datetime import datetime, date
import json

class Serializer:
    def __init__(self):
        self._serializers: Dict[Type, Callable] = {}
        self._deserializers: Dict[Type, Callable] = {}
        self._register_builtin()
    
    def _register_builtin(self):
        self.register(datetime, 
                     lambda dt: dt.isoformat(),
                     lambda s: datetime.fromisoformat(s))
        
        self.register(date,
                     lambda d: d.isoformat(),
                     lambda s: date.fromisoformat(s))
    
    def register(self, type_: Type, serializer: Callable, deserializer: Callable):
        self._serializers[type_] = serializer
        self._deserializers[type_] = deserializer
    
    def serialize(self, obj: Any) -> Any:
        if obj is None:
            return None
        
        obj_type = type(obj)
        
        if obj_type in self._serializers:
            return self._serializers[obj_type](obj)
        
        if isinstance(obj, (str, int, float, bool)):
            return obj
        
        if isinstance(obj, (list, tuple)):
            return [self.serialize(item) for item in obj]
        
        if isinstance(obj, dict):
            return {k: self.serialize(v) for k, v in obj.items()}
        
        if is_dataclass(obj):
            return self._serialize_dataclass(obj)
        
        if hasattr(obj, '__dict__'):
            return self.serialize(obj.__dict__)
        
        return str(obj)
    
    def _serialize_dataclass(self, obj: Any) -> dict:
        result = {'__type__': type(obj).__name__}
        
        for field_name, field_value in obj.__dict__.items():
            result[field_name] = self.serialize(field_value)
        
        return result
    
    def deserialize(self, data: Any, target_type: Type = None) -> Any:
        if data is None:
            return None
        
        if target_type and target_type in self._deserializers:
            return self._deserializers[target_type](data)
        
        if isinstance(data, (str, int, float, bool)):
            return data
        
        if isinstance(data, list):
            return [self.deserialize(item) for item in data]
        
        if isinstance(data, dict):
            if '__type__' in data:
                return self._deserialize_typed(data)
            return {k: self.deserialize(v) for k, v in data.items()}
        
        return data
    
    def _deserialize_typed(self, data: dict) -> Any:
        type_name = data.pop('__type__')
        
        return data

class Field:
    def __init__(self, name: str = None, type_: Type = None, 
                 required: bool = True, default: Any = None):
        self.name = name
        self.type = type_
        self.required = required
        self.default = default

class ModelMeta(type):
    def __new__(mcs, name: str, bases: tuple, namespace: dict):
        cls = super().__new__(mcs, name, bases, namespace)
        
        fields = {}
        for key, value in namespace.items():
            if isinstance(value, Field):
                value.name = key
                fields[key] = value
        
        cls._fields = fields
        
        return cls

class Model(metaclass=ModelMeta):
    def __init__(self, **kwargs):
        for name, field in self._fields.items():
            value = kwargs.get(name, field.default)
            setattr(self, name, value)
    
    def to_dict(self) -> dict:
        result = {}
        for name in self._fields:
            result[name] = getattr(self, name)
        return result
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

class JSONSerializer:
    @staticmethod
    def dumps(obj: Any, indent: int = None) -> str:
        return json.dumps(obj, indent=indent, ensure_ascii=False, default=str)
    
    @staticmethod
    def loads(s: str) -> Any:
        return json.loads(s)

class XMLSerializer:
    @staticmethod
    def to_xml(obj: Any, root_name: str = "root") -> str:
        def convert(value, name: str) -> str:
            if isinstance(value, dict):
                items = "".join(convert(v, k) for k, v in value.items())
                return f"<{name}>{items}</{name}>"
            elif isinstance(value, (list, tuple)):
                items = "".join(convert(item, "item") for item in value)
                return f"<{name}>{items}</{name}>"
            else:
                return f"<{name}>{value}</{name}>"
        
        return f'<?xml version="1.0" encoding="UTF-8"?>\n{convert(obj, root_name)}'
    
    @staticmethod
    def from_xml(xml_str: str) -> dict:
        import xml.etree.ElementTree as ET
        
        def parse(element):
            if len(element) == 0:
                return element.text
            
            result = {}
            for child in element:
                child_data = parse(child)
                if child.tag in result:
                    if not isinstance(result[child.tag], list):
                        result[child.tag] = [result[child.tag]]
                    result[child.tag].append(child_data)
                else:
                    result[child.tag] = child_data
            
            return result
        
        root = ET.fromstring(xml_str)
        return parse(root)

class YAMLSerializer:
    @staticmethod
    def dumps(obj: Any) -> str:
        lines = []
        
        def convert(value, indent: int = 0):
            prefix = "  " * indent
            
            if isinstance(value, dict):
                for k, v in value.items():
                    if isinstance(v, (dict, list)):
                        lines.append(f"{prefix}{k}:")
                        convert(v, indent + 1)
                    else:
                        lines.append(f"{prefix}{k}: {v}")
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        lines.append(f"{prefix}-")
                        convert(item, indent + 1)
                    else:
                        lines.append(f"{prefix}- {item}")
        
        convert(obj)
        return "\n".join(lines)

def main():
    print("=== 基本序列化 ===")
    serializer = Serializer()
    
    data = {
        'name': '张三',
        'age': 25,
        'created_at': datetime(2024, 1, 1, 12, 0, 0),
        'tags': ['python', 'developer']
    }
    
    serialized = serializer.serialize(data)
    print(f"序列化: {serialized}")
    
    print("\n=== JSON序列化 ===")
    json_str = JSONSerializer.dumps(data, indent=2)
    print(json_str)
    
    print("\n=== XML序列化 ===")
    xml_str = XMLSerializer.to_xml(data, "user")
    print(xml_str)
    
    print("\n=== YAML序列化 ===")
    yaml_str = YAMLSerializer.dumps(data)
    print(yaml_str)
    
    print("\n=== Model序列化 ===")
    class User(Model):
        id = Field(type_=int)
        name = Field(type_=str)
        email = Field(type_=str, required=False, default="")
    
    user = User(id=1, name="李四", email="li@example.com")
    print(f"字典: {user.to_dict()}")
    
    user2 = User.from_dict({'id': 2, 'name': '王五', 'email': 'wang@example.com'})
    print(f"从字典创建: {user2.name}")


if __name__ == "__main__":
    main()
