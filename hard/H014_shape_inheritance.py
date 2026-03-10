# -----------------------------
# 题目：继承实现图形类。
# 描述：使用继承实现圆形、矩形等图形类。
# -----------------------------

class Shape:
    def area(self):
        raise NotImplementedError
    
    def perimeter(self):
        raise NotImplementedError

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    
    def area(self):
        return 3.14 * self.radius ** 2
    
    def perimeter(self):
        return 2 * 3.14 * self.radius

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def area(self):
        return self.width * self.height
    
    def perimeter(self):
        return 2 * (self.width + self.height)

def main():
    circle = Circle(5)
    rectangle = Rectangle(4, 6)
    print(f"圆形面积: {circle.area():.2f}, 周长: {circle.perimeter():.2f}")
    print(f"矩形面积: {rectangle.area()}, 周长: {rectangle.perimeter()}")


if __name__ == "__main__":
    main()
