# -----------------------------
# 题目：类的属性和方法。
# 描述：定义类 Calculator，包含属性 result，以及方法 add(), subtract(), multiply(), divide()。
# -----------------------------

class Calculator:
    def __init__(self):
        self.result = 0
    
    def add(self, x):
        self.result += x
        return self
    
    def subtract(self, x):
        self.result -= x
        return self
    
    def multiply(self, x):
        self.result *= x
        return self
    
    def divide(self, x):
        if x != 0:
            self.result /= x
        return self
    
    def clear(self):
        self.result = 0
        return self


def main():
    calc = Calculator()
    result = calc.add(10).multiply(3).subtract(5).result
    print(f"(10 + 3 - 5) = {result}")


if __name__ == "__main__":
    main()


# ========== 详细解析 ==========
# 方法可以返回 self，实现链式调用
# 链式调用让代码更简洁易读