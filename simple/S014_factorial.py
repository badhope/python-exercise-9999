# -----------------------------
# 题目：阶乘计算。
# 描述：计算n的阶乘。
# -----------------------------

def factorial(n):
    if n <= 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

def main():
    print(f"5! = {factorial(5)}")
    print(f"10! = {factorial(10)}")


if __name__ == "__main__":
    main()
