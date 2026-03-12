# -----------------------------
# 题目：实现属性装饰器。
# 描述：使用property实现计算属性和延迟加载。
# -----------------------------

class LazyProperty:
    def __init__(self, func):
        self.func = func
        self.attr_name = func.__name__
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        value = self.func(obj)
        obj.__dict__[self.attr_name] = value
        return value

class Circle:
    def __init__(self, radius):
        self.radius = radius
    
    @property
    def diameter(self):
        return 2 * self.radius
    
    @property
    def area(self):
        return 3.14159 * self.radius ** 2
    
    @LazyProperty
    def expensive_calculation(self):
        print("执行耗时计算...")
        return sum(i ** 2 for i in range(10000))

def main():
    circle = Circle(5)
    print(f"半径: {circle.radius}")
    print(f"直径: {circle.diameter}")
    print(f"面积: {circle.area:.2f}")
    print(f"计算结果: {circle.expensive_calculation}")


if __name__ == "__main__":
    main()
