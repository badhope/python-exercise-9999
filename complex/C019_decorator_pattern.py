# -----------------------------
# 题目：装饰器模式实现日志记录。
# -----------------------------

def log_decorator(func):
    def wrapper(*args, **kwargs):
        print(f"[日志] 调用函数: {func.__name__}")
        result = func(*args, **kwargs)
        print(f"[日志] 函数返回: {result}")
        return result
    return wrapper

def timing_decorator(func):
    import time
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"[性能] {func.__name__} 执行时间: {time.time() - start:.4f}秒")
        return result
    return wrapper

@log_decorator
@timing_decorator
def add(a, b):
    return a + b

@log_decorator
def multiply(a, b):
    return a * b

def main():
    print(add(3, 5))
    print(multiply(4, 7))


if __name__ == "__main__":
    main()
