# -----------------------------
# 题目：绝对值计算。
# 描述：计算一个数的绝对值（不使用abs函数）。
# -----------------------------

def my_abs(n):
    return n if n >= 0 else -n

def main():
    print(f"my_abs(-5) = {my_abs(-5)}")
    print(f"my_abs(10) = {my_abs(10)}")
    print(f"my_abs(0) = {my_abs(0)}")


if __name__ == "__main__":
    main()
