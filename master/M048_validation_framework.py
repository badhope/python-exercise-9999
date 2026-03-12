# -----------------------------
# 题目：实现数据验证框架。
# 描述：支持字段验证、自定义规则、错误消息。
# -----------------------------

import re
from typing import Dict, Any, List, Optional, Callable, Type
from dataclasses import dataclass, field
from enum import Enum

class ValidationError(Exception):
    def __init__(self, errors: Dict[str, List[str]]):
        self.errors = errors
        super().__init__(str(errors))

@dataclass
class FieldError:
    field: str
    message: str
    code: str

class Validator:
    def __init__(self):
        self._rules: List[Callable[[Any], Optional[str]]] = []
    
    def required(self, message: str = "此字段为必填项"):
        def rule(value):
            if value is None or (isinstance(value, str) and not value.strip()):
                return message
            return None
        self._rules.append(rule)
        return self
    
    def min_length(self, length: int, message: str = None):
        message = message or f"长度不能少于{length}个字符"
        def rule(value):
            if value is not None and len(str(value)) < length:
                return message
            return None
        self._rules.append(rule)
        return self
    
    def max_length(self, length: int, message: str = None):
        message = message or f"长度不能超过{length}个字符"
        def rule(value):
            if value is not None and len(str(value)) > length:
                return message
            return None
        self._rules.append(rule)
        return self
    
    def email(self, message: str = "请输入有效的邮箱地址"):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        def rule(value):
            if value is not None and not re.match(pattern, str(value)):
                return message
            return None
        self._rules.append(rule)
        return self
    
    def phone(self, message: str = "请输入有效的手机号码"):
        pattern = r'^1[3-9]\d{9}$'
        def rule(value):
            if value is not None and not re.match(pattern, str(value)):
                return message
            return None
        self._rules.append(rule)
        return self
    
    def min_value(self, min_val: Any, message: str = None):
        message = message or f"值不能小于{min_val}"
        def rule(value):
            if value is not None and value < min_val:
                return message
            return None
        self._rules.append(rule)
        return self
    
    def max_value(self, max_val: Any, message: str = None):
        message = message or f"值不能大于{max_val}"
        def rule(value):
            if value is not None and value > max_val:
                return message
            return None
        self._rules.append(rule)
        return self
    
    def pattern(self, regex: str, message: str = "格式不正确"):
        compiled = re.compile(regex)
        def rule(value):
            if value is not None and not compiled.match(str(value)):
                return message
            return None
        self._rules.append(rule)
        return self
    
    def custom(self, validator: Callable[[Any], Optional[str]]):
        self._rules.append(validator)
        return self
    
    def validate(self, value: Any) -> List[str]:
        errors = []
        for rule in self._rules:
            error = rule(value)
            if error:
                errors.append(error)
        return errors

class Schema:
    def __init__(self):
        self._fields: Dict[str, Validator] = {}
        self._messages: Dict[str, Dict[str, str]] = {}
    
    def field(self, name: str) -> Validator:
        validator = Validator()
        self._fields[name] = validator
        return validator
    
    def add_field(self, name: str, validator: Validator):
        self._fields[name] = validator
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        errors = {}
        
        for field_name, validator in self._fields.items():
            value = data.get(field_name)
            field_errors = validator.validate(value)
            if field_errors:
                errors[field_name] = field_errors
        
        return errors
    
    def is_valid(self, data: Dict[str, Any]) -> bool:
        return len(self.validate(data)) == 0
    
    def assert_valid(self, data: Dict[str, Any]):
        errors = self.validate(data)
        if errors:
            raise ValidationError(errors)

class ModelValidator:
    def __init__(self):
        self._validators: Dict[Type, Schema] = {}
    
    def register(self, model_class: Type, schema: Schema):
        self._validators[model_class] = schema
    
    def validate(self, instance) -> Dict[str, List[str]]:
        schema = self._validators.get(type(instance))
        if not schema:
            return {}
        
        data = {
            attr: getattr(instance, attr)
            for attr in dir(instance)
            if not attr.startswith('_')
        }
        
        return schema.validate(data)

def validate(schema: Schema):
    def decorator(func):
        def wrapper(data: Dict[str, Any], *args, **kwargs):
            errors = schema.validate(data)
            if errors:
                raise ValidationError(errors)
            return func(data, *args, **kwargs)
        return wrapper
    return decorator

def main():
    user_schema = Schema()
    user_schema.field("username").required("用户名不能为空").min_length(3).max_length(20)
    user_schema.field("email").required().email()
    user_schema.field("phone").phone()
    user_schema.field("age").min_value(0).max_value(150)
    user_schema.field("password").required().min_length(8).pattern(r'^(?=.*[A-Za-z])(?=.*\d)', "密码必须包含字母和数字")
    
    valid_data = {
        "username": "zhangsan",
        "email": "zhang@example.com",
        "phone": "13800138000",
        "age": 25,
        "password": "abc123456"
    }
    
    print("验证有效数据:")
    errors = user_schema.validate(valid_data)
    print(f"  错误: {errors if errors else '无'}")
    
    invalid_data = {
        "username": "ab",
        "email": "invalid-email",
        "phone": "12345",
        "age": -5,
        "password": "123"
    }
    
    print("\n验证无效数据:")
    errors = user_schema.validate(invalid_data)
    for field, msgs in errors.items():
        print(f"  {field}: {msgs}")
    
    @validate(user_schema)
    def create_user(data: Dict[str, Any]):
        return f"创建用户: {data['username']}"
    
    print("\n使用装饰器验证:")
    try:
        result = create_user(valid_data)
        print(f"  {result}")
    except ValidationError as e:
        print(f"  验证失败: {e.errors}")

if __name__ == "__main__":
    main()
