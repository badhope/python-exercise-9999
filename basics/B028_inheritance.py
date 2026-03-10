# -----------------------------
# 题目：类的继承。
# 描述：定义基类 Animal，以及子类 Dog 继承自 Animal，实现多态。
# -----------------------------

class Animal:
    def __init__(self, name):
        self.name = name
    
    def speak(self):
        raise NotImplementedError("子类必须重写 speak 方法")


class Dog(Animal):
    def speak(self):
        return f"{self.name} says Woof!"


class Cat(Animal):
    def speak(self):
        return f"{self.name} says Meow!"


def main():
    dog = Dog("Buddy")
    cat = Cat("Whiskers")
    
    print(dog.speak())
    print(cat.speak())
    
    animals = [dog, cat]
    for animal in animals:
        print(animal.speak())


if __name__ == "__main__":
    main()


# ========== 详细解析 ==========
# 继承：子类继承父类的属性和方法
# 重写：子类可以重写父类的方法
# 多态：不同对象对同一消息做出不同响应