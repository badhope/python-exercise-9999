# -----------------------------
# 题目：原型模式实现图形克隆。
# -----------------------------

import copy

class Shape:
    def __init__(self, color="black"):
        self.color = color
    
    def clone(self):
        return copy.deepcopy(self)
    
    def draw(self):
        pass

class Circle(Shape):
    def __init__(self, x, y, radius, color="black"):
        super().__init__(color)
        self.x = x
        self.y = y
        self.radius = radius
    
    def draw(self):
        return f"圆形(位置:{self.x},{self.y}, 半径:{self.radius}, 颜色:{self.color})"
    
    def move(self, dx, dy):
        self.x += dx
        self.y += dy

class Rectangle(Shape):
    def __init__(self, x, y, width, height, color="black"):
        super().__init__(color)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    def draw(self):
        return f"矩形(位置:{self.x},{self.y}, 大小:{self.width}x{self.height}, 颜色:{self.color})"
    
    def resize(self, w, h):
        self.width = w
        self.height = h

class Triangle(Shape):
    def __init__(self, points, color="black"):
        super().__init__(color)
        self.points = points
    
    def draw(self):
        return f"三角形(顶点:{self.points}, 颜色:{self.color})"

class ShapeRegistry:
    def __init__(self):
        self._prototypes = {}
    
    def register(self, name, prototype):
        self._prototypes[name] = prototype
    
    def unregister(self, name):
        if name in self._prototypes:
            del self._prototypes[name]
    
    def clone(self, name, **kwargs):
        prototype = self._prototypes.get(name)
        if prototype:
            cloned = prototype.clone()
            for key, value in kwargs.items():
                if hasattr(cloned, key):
                    setattr(cloned, key, value)
            return cloned
        return None
    
    def get_prototype_names(self):
        return list(self._prototypes.keys())

class Canvas:
    def __init__(self):
        self.shapes = []
    
    def add_shape(self, shape):
        self.shapes.append(shape)
    
    def draw_all(self):
        return [shape.draw() for shape in self.shapes]
    
    def duplicate_shape(self, index):
        if 0 <= index < len(self.shapes):
            cloned = self.shapes[index].clone()
            self.shapes.append(cloned)
            return cloned
        return None

def main():
    registry = ShapeRegistry()
    
    registry.register("small_circle", Circle(0, 0, 10, "red"))
    registry.register("big_circle", Circle(0, 0, 50, "blue"))
    registry.register("button", Rectangle(0, 0, 100, 40, "gray"))
    registry.register("card", Rectangle(0, 0, 200, 150, "white"))
    
    canvas = Canvas()
    
    circle1 = registry.clone("small_circle", x=100, y=100)
    canvas.add_shape(circle1)
    
    circle2 = registry.clone("big_circle", x=200, y=200)
    canvas.add_shape(circle2)
    
    button1 = registry.clone("button", x=50, y=50)
    canvas.add_shape(button1)
    
    button2 = registry.clone("button", x=200, y=50)
    canvas.add_shape(button2)
    
    card = registry.clone("card", x=300, y=100)
    canvas.add_shape(card)
    
    print("=== 原始图形 ===")
    for shape in canvas.draw_all():
        print(shape)
    
    print("\n=== 复制第一个图形 ===")
    duplicated = canvas.duplicate_shape(0)
    if duplicated:
        duplicated.move(50, 50)
        print(duplicated.draw())
    
    print("\n=== 所有图形 ===")
    for shape in canvas.draw_all():
        print(shape)
    
    print(f"\n可用原型: {registry.get_prototype_names()}")


if __name__ == "__main__":
    main()
