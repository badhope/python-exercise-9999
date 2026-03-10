# -----------------------------
# 题目：计算第n个斐波那契数。
# 描述：计算斐波那契数列的第n个数。
# -----------------------------

def fib(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

def main():
    print(f"第10个斐波那契数: {fib(10)}")


if __name__ == "__main__":
    main()
