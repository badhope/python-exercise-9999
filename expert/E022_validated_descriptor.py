# -----------------------------
# 题目：实现属性描述符。
# -----------------------------

from typing import Any, Type

class ValidatedAttribute:
    def __init__(self, name: str = None, validator: callable = None):
        self.name = name
        self.validator = validator
    
    def __set_name__(self, owner: Type, name: str):
        self.name = name
    
    def __get__(self, obj: Any, owner: Type = None) -> Any:
        if obj is None:
            return self
        return obj.__dict__.get(self.name)
    
    def __set__(self, obj: Any, value: Any):
        if self.validator and not self.validator(value):
            raise ValueError(f"无效的值: {value}")
        obj.__dict__[self.name] = value

class TypedAttribute:
    def __init__(self, expected_type: Type, default: Any = None):
        self.expected_type = expected_type
        self.default = default
        self.name = None
    
    def __set_name__(self, owner: Type, name: str):
        self.name = name
    
    def __get__(self, obj: Any, owner: Type = None) -> Any:
        if obj is None:
            return self
        return obj.__dict__.get(self.name, self.default)
    
    def __set__(self, obj: Any, value: Any):
        if not isinstance(value, self.expected_type):
            raise TypeError(f"期望类型 {self.expected_type.__name__}, 实际类型 {type(value).__name__}")
        obj.__dict__[self.name] = value

class RangeAttribute:
    def __init__(self, min_val: float = None, max_val: float = None, default: float = 0):
        self.min_val = min_val
        self.max_val = max_val
        self.default = default
        self.name = None
    
    def __set_name__(self, owner: Type, name: str):
        self.name = name
    
    def __get__(self, obj: Any, owner: Type = None) -> Any:
        if obj is None:
            return self
        return obj.__dict__.get(self.name, self.default)
    
    def __set__(self, obj: Any, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError("值必须是数字")
        
        if self.min_val is not None and value < self.min_val:
            raise ValueError(f"值不能小于 {self.min_val}")
        
        if self.max_val is not None and value > self.max_val:
            raise ValueError(f"值不能大于 {self.max_val}")
        
        obj.__dict__[self.name] = value

class ReadOnlyAttribute:
    def __init__(self, default: Any = None):
        self.default = default
        self.name = None
        self._initialized = set()
    
    def __set_name__(self, owner: Type, name: str):
        self.name = name
    
    def __get__(self, obj: Any, owner: Type = None) -> Any:
        if obj is None:
            return self
        return obj.__dict__.get(self.name, self.default)
    
    def __set__(self, obj: Any, value: Any):
        obj_id = id(obj)
        if obj_id in self._initialized:
            raise AttributeError(f"属性 {self.name} 是只读的")
        
        obj.__dict__[self.name] = value
        self._initialized.add(obj_id)

class Person:
    name = TypedAttribute(str, "")
    age = RangeAttribute(0, 150, 0)
    email = ValidatedAttribute(validator=lambda x: '@' in str(x) if x else True)
    id = ReadOnlyAttribute()
    
    def __init__(self, id: int, name: str, age: int, email: str = ""):
        self.id = id
        self.name = name
        self.age = age
        self.email = email

class Product:
    price = RangeAttribute(0, 100000, 0)
    stock = RangeAttribute(0, 10000, 0)
    name = TypedAttribute(str, "")
    
    def __init__(self, name: str, price: float, stock: int):
        self.name = name
        self.price = price
        self.stock = stock

def main():
    print("=== Person类测试 ===")
    person = Person(1, "张三", 25, "zhang@example.com")
    print(f"ID: {person.id}, 姓名: {person.name}, 年龄: {person.age}, 邮箱: {person.email}")
    
    print("\n=== 类型验证 ===")
    try:
        person.name = 123
    except TypeError as e:
        print(f"错误: {e}")
    
    print("\n=== 范围验证 ===")
    try:
        person.age = 200
    except ValueError as e:
        print(f"错误: {e}")
    
    print("\n=== 自定义验证 ===")
    try:
        person.email = "invalid-email"
    except ValueError as e:
        print(f"错误: {e}")
    
    print("\n=== 只读属性 ===")
    try:
        person.id = 2
    except AttributeError as e:
        print(f"错误: {e}")
    
    print("\n=== Product类测试 ===")
    product = Product("iPhone", 999, 100)
    print(f"产品: {product.name}, 价格: {product.price}, 库存: {product.stock}")
    
    product.price = 899
    print(f"更新价格: {product.price}")


if __name__ == "__main__":
    main()
