# -----------------------------
# 题目：实现简单的验证器。
# 描述：支持数据验证规则定义和检查。
# -----------------------------

class ValidationError(Exception):
    pass

class Validator:
    def __init__(self):
        self.rules = []
    
    def required(self):
        self.rules.append(lambda x: x is not None and x != "")
        return self
    
    def min_length(self, length):
        self.rules.append(lambda x: len(str(x)) >= length if x else True)
        return self
    
    def max_length(self, length):
        self.rules.append(lambda x: len(str(x)) <= length if x else True)
        return self
    
    def pattern(self, regex):
        import re
        self.rules.append(lambda x: bool(re.match(regex, str(x))) if x else True)
        return self
    
    def validate(self, value):
        for rule in self.rules:
            if not rule(value):
                raise ValidationError(f"验证失败: {value}")
        return True

class Schema:
    def __init__(self):
        self.fields = {}
    
    def field(self, name):
        validator = Validator()
        self.fields[name] = validator
        return validator
    
    def validate(self, data):
        errors = {}
        for name, validator in self.fields.items():
            try:
                validator.validate(data.get(name))
            except ValidationError as e:
                errors[name] = str(e)
        return errors if errors else None

def main():
    schema = Schema()
    schema.field("username").required().min_length(3).max_length(20)
    schema.field("email").required().pattern(r'^[\w.-]+@[\w.-]+\.\w+$')
    
    data = {"username": "ab", "email": "invalid"}
    errors = schema.validate(data)
    if errors:
        print(f"验证错误: {errors}")
    else:
        print("验证通过")


if __name__ == "__main__":
    main()
