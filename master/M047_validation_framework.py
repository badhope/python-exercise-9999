# -----------------------------
# 题目：实现验证框架。
# -----------------------------

import re
from enum import Enum

class ValidationType(Enum):
    REQUIRED = "required"
    EMAIL = "email"
    MIN_LENGTH = "min_length"
    MAX_LENGTH = "max_length"
    PATTERN = "pattern"
    RANGE = "range"

class ValidationRule:
    def __init__(self, validation_type, *args, **kwargs):
        self.type = validation_type
        self.args = args
        self.kwargs = kwargs
    
    def validate(self, value):
        if self.type == ValidationType.REQUIRED:
            return value is not None and value != ""
        
        if value is None or value == "":
            return True
        
        if self.type == ValidationType.EMAIL:
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return bool(re.match(pattern, value))
        
        if self.type == ValidationType.MIN_LENGTH:
            return len(value) >= self.args[0]
        
        if self.type == ValidationType.MAX_LENGTH:
            return len(value) <= self.args[0]
        
        if self.type == ValidationType.PATTERN:
            return bool(re.match(self.args[0], value))
        
        if self.type == ValidationType.RANGE:
            return self.args[0] <= value <= self.args[1]
        
        return True

class Validator:
    def __init__(self):
        self.rules = {}
    
    def add_rule(self, field, rule):
        if field not in self.rules:
            self.rules[field] = []
        self.rules[field].append(rule)
    
    def validate(self, data):
        errors = {}
        
        for field, rules in self.rules.items():
            value = data.get(field)
            for rule in rules:
                if not rule.validate(value):
                    if field not in errors:
                        errors[field] = []
                    errors[field].append(f"Validation failed for {field}: {rule.type.value}")
        
        return len(errors) == 0, errors

if __name__ == "__main__":
    validator = Validator()
    validator.add_rule("username", ValidationRule(ValidationType.REQUIRED))
    validator.add_rule("username", ValidationRule(ValidationType.MIN_LENGTH, 3))
    validator.add_rule("email", ValidationRule(ValidationType.REQUIRED))
    validator.add_rule("email", ValidationRule(ValidationType.EMAIL))
    validator.add_rule("age", ValidationRule(ValidationType.RANGE, 0, 150))
    
    valid_data = {"username": "john", "email": "john@example.com", "age": 25}
    valid, errors = validator.validate(valid_data)
    print(f"Valid: {valid}, Errors: {errors}")
    
    invalid_data = {"username": "jo", "email": "invalid", "age": 200}
    valid, errors = validator.validate(invalid_data)
    print(f"Valid: {valid}, Errors: {errors}")
