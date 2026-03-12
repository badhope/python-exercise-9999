# -----------------------------
# 题目：实现简单的序列化器。
# -----------------------------

import json
from typing import Any, Dict, List, Type, get_type_hints
from dataclasses import dataclass, is_dataclass
from datetime import datetime

class Serializer:
    def __init__(self):
        self._serializers = {}
        self._register_builtin()
    
    def _register_builtin(self):
        self._serializers[datetime] = {
            'serialize': lambda dt: dt.isoformat(),
            'deserialize': lambda s: datetime.fromisoformat(s)
        }
    
    def register(self, type_class: Type, serialize_fn, deserialize_fn):
        self._serializers[type_class] = {
            'serialize': serialize_fn,
            'deserialize': deserialize_fn
        }
    
    def serialize(self, obj: Any) -> Any:
        if obj is None:
            return None
        
        obj_type = type(obj)
        
        if obj_type in self._serializers:
            return self._serializers[obj_type]['serialize'](obj)
        
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
    
    def _serialize_dataclass(self, obj) -> Dict:
        result = {'__type__': obj.__class__.__name__}
        for field in obj.__dataclass_fields__:
            result[field] = self.serialize(getattr(obj, field))
        return result
    
    def deserialize(self, data: Any, target_type: Type = None) -> Any:
        if data is None:
            return None
        
        if target_type and target_type in self._serializers:
            return self._serializers[target_type]['deserialize'](data)
        
        if isinstance(data, (str, int, float, bool)):
            return data
        
        if isinstance(data, list):
            return [self.deserialize(item) for item in data]
        
        if isinstance(data, dict):
            if '__type__' in data:
                return self._deserialize_typed(data)
            return {k: self.deserialize(v) for k, v in data.items()}
        
        return data
    
    def _deserialize_typed(self, data: Dict) -> Any:
        return data
    
    def to_json(self, obj: Any) -> str:
        return json.dumps(self.serialize(obj), ensure_ascii=False, indent=2)
    
    def from_json(self, json_str: str, target_type: Type = None) -> Any:
        data = json.loads(json_str)
        return self.deserialize(data, target_type)

class ModelSerializer:
    def __init__(self, model_class: Type):
        self.model_class = model_class
        self.fields = {}
    
    def add_field(self, name: str, field_type: Type = None, required: bool = True):
        self.fields[name] = {
            'type': field_type,
            'required': required
        }
        return self
    
    def serialize(self, obj: Any) -> Dict:
        result = {}
        for field_name, field_info in self.fields.items():
            value = getattr(obj, field_name, None)
            if value is not None:
                result[field_name] = value
        return result
    
    def deserialize(self, data: Dict) -> Any:
        kwargs = {}
        for field_name, field_info in self.fields.items():
            if field_name in data:
                kwargs[field_name] = data[field_name]
            elif field_info['required']:
                raise ValueError(f"缺少必填字段: {field_name}")
        
        return self.model_class(**kwargs)

@dataclass
class User:
    id: int
    name: str
    email: str
    created_at: datetime = None

@dataclass
class Product:
    id: int
    name: str
    price: float
    tags: List[str] = None

def main():
    serializer = Serializer()
    
    print("=== 序列化基本类型 ===")
    data = {
        'name': '张三',
        'age': 25,
        'scores': [90, 85, 95],
        'active': True
    }
    json_str = serializer.to_json(data)
    print(json_str)
    
    print("\n=== 序列化日期时间 ===")
    now = datetime.now()
    serialized = serializer.serialize({'time': now})
    print(f"序列化后: {serialized}")
    
    print("\n=== 序列化数据类 ===")
    user = User(id=1, name='张三', email='zhang@example.com', created_at=datetime.now())
    user_json = serializer.to_json(user)
    print(user_json)
    
    print("\n=== 使用ModelSerializer ===")
    user_serializer = ModelSerializer(User)
    user_serializer.add_field('id', int).add_field('name', str).add_field('email', str)
    
    user_data = {'id': 2, 'name': '李四', 'email': 'li@example.com'}
    new_user = user_serializer.deserialize(user_data)
    print(f"反序列化: id={new_user.id}, name={new_user.name}")
    
    serialized_user = user_serializer.serialize(new_user)
    print(f"序列化: {serialized_user}")


if __name__ == "__main__":
    main()
