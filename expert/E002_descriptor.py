# -----------------------------
# 题目：实现描述符协议。
# 描述：使用描述符实现属性验证。
# -----------------------------

class ValidatedAttribute:
    def __init__(self, validator, name=None):
        self.validator = validator
        self.name = name
    
    def __set_name__(self, owner, name):
        self.name = name
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj.__dict__.get(self.name)
    
    def __set__(self, obj, value):
        if not self.validator(value):
            raise ValueError(f"无效值: {value}")
        obj.__dict__[self.name] = value

def is_positive(value):
    return isinstance(value, (int, float)) and value > 0

def is_non_empty_string(value):
    return isinstance(value, str) and len(value) > 0

class Product:
    name = ValidatedAttribute(is_non_empty_string)
    price = ValidatedAttribute(is_positive)
    
    def __init__(self, name, price):
        self.name = name
        self.price = price

def main():
    product = Product("笔记本", 5999)
    print(f"商品: {product.name}, 价格: {product.price}")
    
    try:
        product.price = -100
    except ValueError as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    main()
