# -----------------------------
# 题目：实现简单的序列化系统。
# 描述：支持对象到JSON的序列化和反序列化。
# -----------------------------

import json

class Serializable:
    def to_dict(self):
        return self.__dict__.copy()
    
    @classmethod
    def from_dict(cls, data):
        obj = cls.__new__(cls)
        obj.__dict__.update(data)
        return obj

class JsonSerializer:
    @staticmethod
    def serialize(obj):
        if hasattr(obj, 'to_dict'):
            return json.dumps(obj.to_dict(), ensure_ascii=False)
        return json.dumps(obj, ensure_ascii=False)
    
    @staticmethod
    def deserialize(json_str, cls=None):
        data = json.loads(json_str)
        if cls and hasattr(cls, 'from_dict'):
            return cls.from_dict(data)
        return data

class User(Serializable):
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def __str__(self):
        return f"User(name={self.name}, age={self.age})"

def main():
    user = User("张三", 25)
    json_str = JsonSerializer.serialize(user)
    print(f"序列化: {json_str}")
    
    restored = JsonSerializer.deserialize(json_str, User)
    print(f"反序列化: {restored}")


if __name__ == "__main__":
    main()
