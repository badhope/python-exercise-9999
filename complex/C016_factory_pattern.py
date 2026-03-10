# -----------------------------
# 题目：工厂模式实现图形生成器。
# -----------------------------

class Shape:
    def draw(self):
        pass

class Circle(Shape):
    def draw(self):
        return "绘制圆形"

class Rectangle(Shape):
    def draw(self):
        return "绘制矩形"

class Triangle(Shape):
    def draw(self):
        return "绘制三角形"

class ShapeFactory:
    _shapes = {
        "circle": Circle,
        "rectangle": Rectangle,
        "triangle": Triangle
    }
    
    @classmethod
    def create_shape(cls, shape_type):
        shape_class = cls._shapes.get(shape_type)
        if shape_class:
            return shape_class()
        return None

def main():
    shapes = ["circle", "rectangle", "triangle", "square"]
    for shape_type in shapes:
        shape = ShapeFactory.create_shape(shape_type)
        if shape:
            print(f"{shape_type}: {shape.draw()}")
        else:
            print(f"{shape_type}: 未知图形")


if __name__ == "__main__":
    main()
