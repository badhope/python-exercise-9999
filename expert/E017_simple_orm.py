# -----------------------------
# 题目：实现简易ORM框架。
# -----------------------------

class Field:
    def __init__(self, field_type):
        self.field_type = field_type
        self.name = None
    
    def __set_name__(self, owner, name):
        self.name = name

class CharField(Field):
    def __init__(self, max_length=255):
        super().__init__("VARCHAR")
        self.max_length = max_length

class IntegerField(Field):
    def __init__(self):
        super().__init__("INTEGER")

class ModelMeta(type):
    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        if name != "Model":
            cls._table = name.lower()
            cls._fields = {}
            for attr_name, attr_value in namespace.items():
                if isinstance(attr_value, Field):
                    cls._fields[attr_name] = attr_value
        return cls

class Model(metaclass=ModelMeta):
    _table = None
    _fields = {}
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @classmethod
    def create_table(cls):
        columns = [f"{name} {field.field_type}" for name, field in cls._fields.items()]
        print(f"CREATE TABLE {cls._table} ({', '.join(columns)})")

class User(Model):
    name = CharField(max_length=100)
    age = IntegerField()

def main():
    User.create_table()
    user = User(name="张三", age=25)
    print(f"创建用户: {user.name}, {user.age}")


if __name__ == "__main__":
    main()
