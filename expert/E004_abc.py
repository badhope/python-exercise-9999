# -----------------------------
# 题目：实现抽象基类。
# 描述：使用ABC定义抽象接口。
# -----------------------------

from abc import ABC, abstractmethod

class Animal(ABC):
    @abstractmethod
    def speak(self):
        pass
    
    @abstractmethod
    def move(self):
        pass
    
    def describe(self):
        return f"{self.__class__.__name__}: {self.speak()}"

class Dog(Animal):
    def speak(self):
        return "汪汪"
    
    def move(self):
        return "奔跑"

class Cat(Animal):
    def speak(self):
        return "喵喵"
    
    def move(self):
        return "跳跃"

class Bird(Animal):
    def speak(self):
        return "叽叽"
    
    def move(self):
        return "飞翔"

def main():
    animals = [Dog(), Cat(), Bird()]
    for animal in animals:
        print(animal.describe())


if __name__ == "__main__":
    main()
