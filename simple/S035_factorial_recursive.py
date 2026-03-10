# -----------------------------
# 题目：阶乘（递归）。
# 描述：使用递归计算阶乘。
# -----------------------------

def factorial_recursive(n):
    if n <= 1:
        return 1
    return n * factorial_recursive(n - 1)

def main():
    print(f"5! = {factorial_recursive(5)}")


if __name__ == "__main__":
    main()
