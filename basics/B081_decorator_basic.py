# -----------------------------
# 题目：装饰器基础。
# 描述：创建和应用简单的装饰器。
# -----------------------------

def decorator(func):
    def wrapper():
        print("Before")
        func()
        print("After")
    return wrapper

@decorator
def say_hello():
    print("Hello!")

def main():
    say_hello()


if __name__ == "__main__":
    main()
