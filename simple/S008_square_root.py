# -----------------------------
# 题目：平方根。
# 描述：计算一个非负数的平方根。
# -----------------------------

def square_root(n):
    if n < 0:
        return "错误：不能对负数开平方"
    return n ** 0.5

def main():
    print(f"sqrt(16) = {square_root(16)}")
    print(f"sqrt(2) = {square_root(2):.4f}")
    print(f"sqrt(0) = {square_root(0)}")


if __name__ == "__main__":
    main()
