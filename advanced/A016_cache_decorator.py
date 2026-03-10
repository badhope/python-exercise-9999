# -----------------------------
# 题目：实现简单的缓存装饰器。
# -----------------------------

def memoize(func):
    cache = {}
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    wrapper.cache = cache
    return wrapper

@memoize
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

@memoize
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)

def main():
    print("斐波那契数列:")
    for i in range(10):
        print(f"fib({i}) = {fibonacci(i)}")
    print(f"缓存大小: {len(fibonacci.cache)}")
    print(f"阶乘 5! = {factorial(5)}")


if __name__ == "__main__":
    main()
