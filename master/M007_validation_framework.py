# -----------------------------
# 题目：实现简单的验证框架。
# 描述：支持字段验证、自定义规则、错误消息。
# -----------------------------

class ValidationError(Exception):
    def __init__(self, errors):
        self.errors = errors
        super().__init__(str(errors))

class Field:
    def __init__(self, required=False, message=None):
        self.required = required
        self.message = message
        self.validators = []
    
    def validate(self, value):
        if value is None or value == '':
            if self.required:
                return [self.message or "此字段必填"]
            return []
        
        errors = []
        for validator in self.validators:
            error = validator(value)
            if error:
                errors.append(error)
        return errors

class StringField(Field):
    def __init__(self, min_length=None, max_length=None, **kwargs):
        super().__init__(**kwargs)
        if min_length:
            self.validators.append(lambda v: f"最小长度 {min_length}" if len(v) < min_length else None)
        if max_length:
            self.validators.append(lambda v: f"最大长度 {max_length}" if len(v) > max_length else None)

class IntegerField(Field):
    def __init__(self, min_value=None, max_value=None, **kwargs):
        super().__init__(**kwargs)
        self.validators.append(lambda v: "必须是整数" if not isinstance(v, int) else None)
        if min_value is not None:
            self.validators.append(lambda v: f"最小值 {min_value}" if v < min_value else None)
        if max_value is not None:
            self.validators.append(lambda v: f"最大值 {max_value}" if v > max_value else None)

class EmailField(Field):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        import re
        pattern = r'^[\w.-]+@[\w.-]+\.\w+$'
        self.validators.append(lambda v: "邮箱格式无效" if not re.match(pattern, v) else None)

class Form:
    def __init__(self, data):
        self.data = data
        self.errors = {}
    
    def validate(self):
        self.errors = {}
        for name in dir(self):
            attr = getattr(self, name)
            if isinstance(attr, Field):
                value = self.data.get(name)
                field_errors = attr.validate(value)
                if field_errors:
                    self.errors[name] = field_errors
        return len(self.errors) == 0

class UserForm(Form):
    username = StringField(required=True, min_length=3, max_length=20)
    email = EmailField(required=True)
    age = IntegerField(min_value=0, max_value=150)

def main():
    data = {
        'username': 'ab',
        'email': 'invalid',
        'age': -5
    }
    
    form = UserForm(data)
    if form.validate():
        print("验证通过")
    else:
        print("验证失败:")
        for field, errors in form.errors.items():
            print(f"  {field}: {errors}")


if __name__ == "__main__":
    main()
