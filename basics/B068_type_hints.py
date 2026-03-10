# -----------------------------
# 题目：类型注解。
# 描述：使用类型注解定义函数参数和返回值类型。
# -----------------------------

def greet(name: str) -> str:
    return f"Hello, {name}!"

def add(a: int, b: int) -> int:
    return a + b

def main():
    print(greet("Alice"))
    print(add(3, 4))


if __name__ == "__main__":
    main()
