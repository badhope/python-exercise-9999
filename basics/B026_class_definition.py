# -----------------------------
# 题目：类和对象基础。
# 描述：定义类 Person，包含属性 name, age，以及方法 introduce()。
# -----------------------------

class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def introduce(self):
        return f"My name is {self.name}, I am {self.age} years old."


def main():
    person = Person("Alice", 25)
    print(person.introduce())


if __name__ == "__main__":
    main()


# ========== 详细解析 ==========
# class：定义类的关键字
# __init__：构造方法，创建对象时自动调用
# self：指向实例本身，访问属性和方法时需要