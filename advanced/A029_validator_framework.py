# -----------------------------
# 题目：实现简单的验证器框架。
# -----------------------------

from typing import Any, Dict, List, Callable, Optional
from dataclasses import dataclass

@dataclass
class ValidationError:
    field: str
    message: str
    value: Any

class Validator:
    def __init__(self, field_name: str):
        self.field_name = field_name
        self.rules: List[Callable] = []
    
    def required(self, message: str = "此字段必填"):
        def rule(value: Any) -> Optional[str]:
            if value is None or value == '':
                return message
            return None
        self.rules.append(rule)
        return self
    
    def min_length(self, length: int, message: str = None):
        message = message or f"长度不能少于{length}个字符"
        def rule(value: Any) -> Optional[str]:
            if value is not None and len(str(value)) < length:
                return message
            return None
        self.rules.append(rule)
        return self
    
    def max_length(self, length: int, message: str = None):
        message = message or f"长度不能超过{length}个字符"
        def rule(value: Any) -> Optional[str]:
            if value is not None and len(str(value)) > length:
                return message
            return None
        self.rules.append(rule)
        return self
    
    def email(self, message: str = "邮箱格式不正确"):
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        def rule(value: Any) -> Optional[str]:
            if value is not None and not re.match(pattern, str(value)):
                return message
            return None
        self.rules.append(rule)
        return self
    
    def phone(self, message: str = "手机号格式不正确"):
        import re
        pattern = r'^1[3-9]\d{9}$'
        def rule(value: Any) -> Optional[str]:
            if value is not None and not re.match(pattern, str(value)):
                return message
            return None
        self.rules.append(rule)
        return self
    
    def min_value(self, min_val: Any, message: str = None):
        message = message or f"值不能小于{min_val}"
        def rule(value: Any) -> Optional[str]:
            if value is not None and value < min_val:
                return message
            return None
        self.rules.append(rule)
        return self
    
    def max_value(self, max_val: Any, message: str = None):
        message = message or f"值不能大于{max_val}"
        def rule(value: Any) -> Optional[str]:
            if value is not None and value > max_val:
                return message
            return None
        self.rules.append(rule)
        return self
    
    def pattern(self, regex: str, message: str = "格式不正确"):
        import re
        compiled = re.compile(regex)
        def rule(value: Any) -> Optional[str]:
            if value is not None and not compiled.match(str(value)):
                return message
            return None
        self.rules.append(rule)
        return self
    
    def custom(self, validator: Callable[[Any], Optional[str]]):
        self.rules.append(validator)
        return self
    
    def validate(self, value: Any) -> List[str]:
        errors = []
        for rule in self.rules:
            error = rule(value)
            if error:
                errors.append(error)
        return errors

class Schema:
    def __init__(self):
        self.validators: Dict[str, Validator] = {}
    
    def field(self, name: str) -> Validator:
        validator = Validator(name)
        self.validators[name] = validator
        return validator
    
    def validate(self, data: Dict) -> Dict[str, List[str]]:
        errors = {}
        for field_name, validator in self.validators.items():
            value = data.get(field_name)
            field_errors = validator.validate(value)
            if field_errors:
                errors[field_name] = field_errors
        return errors
    
    def is_valid(self, data: Dict) -> bool:
        return len(self.validate(data)) == 0

class FormValidator:
    def __init__(self):
        self.schemas: Dict[str, Schema] = {}
    
    def register(self, name: str, schema: Schema):
        self.schemas[name] = schema
    
    def validate(self, name: str, data: Dict) -> Dict[str, List[str]]:
        schema = self.schemas.get(name)
        if schema:
            return schema.validate(data)
        return {'_schema': ['验证模式不存在']}

def main():
    user_schema = Schema()
    user_schema.field('username').required().min_length(3).max_length(20)
    user_schema.field('email').required().email()
    user_schema.field('phone').phone()
    user_schema.field('age').min_value(0).max_value(150)
    user_schema.field('password').required().min_length(8).pattern(r'^(?=.*[A-Za-z])(?=.*\d)', "密码必须包含字母和数字")
    
    print("=== 验证有效数据 ===")
    valid_data = {
        'username': 'zhangsan',
        'email': 'zhang@example.com',
        'phone': '13812345678',
        'age': 25,
        'password': 'abc12345'
    }
    errors = user_schema.validate(valid_data)
    print(f"验证结果: {'通过' if not errors else errors}")
    
    print("\n=== 验证无效数据 ===")
    invalid_data = {
        'username': 'ab',
        'email': 'invalid-email',
        'phone': '12345',
        'age': -5,
        'password': '123'
    }
    errors = user_schema.validate(invalid_data)
    for field, messages in errors.items():
        print(f"{field}: {messages}")
    
    print("\n=== 使用FormValidator ===")
    form_validator = FormValidator()
    form_validator.register('user', user_schema)
    
    errors = form_validator.validate('user', invalid_data)
    print(f"表单验证错误数: {len(errors)}")


if __name__ == "__main__":
    main()
