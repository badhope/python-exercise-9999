# -----------------------------
# 题目：斐波那契（递归）。
# 描述：使用递归计算斐波那契数列。
# -----------------------------

def fib_recursive(n):
    if n <= 1:
        return n
    return fib_recursive(n-1) + fib_recursive(n-2)

def main():
    print(f"Fib(10) = {fib_recursive(10)}")


if __name__ == "__main__":
    main()
