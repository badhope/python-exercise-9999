# -----------------------------
# 题目：带参数的装饰器。
# 描述：创建可以接受参数的装饰器。
# -----------------------------

def repeat(times):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(times):
                func(*args, **kwargs)
        return wrapper
    return decorator

@repeat(times=3)
def say_hello():
    print("Hello!")

def main():
    say_hello()


if __name__ == "__main__":
    main()
