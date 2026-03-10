# -----------------------------
# 题目：求平方根。
# 描述：使用牛顿迭代法求平方根。
# -----------------------------

def sqrt_newton(n):
    if n < 0:
        return None
    x = n
    while True:
        root = (x + n / x) / 2
        if abs(root - x) < 0.0001:
            return root
        x = root

def main():
    print(f"sqrt(16) = {sqrt_newton(16):.4f}")


if __name__ == "__main__":
    main()
