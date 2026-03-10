# -----------------------------
# 题目：计算阶乘（循环）。
# 描述：使用循环计算阶乘。
# -----------------------------

def factorial_iterative(n):
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

def main():
    print(f"5! = {factorial_iterative(5)}")


if __name__ == "__main__":
    main()
