# -----------------------------
# 题目：求和函数。
# 描述：计算1到n的所有整数之和。
# -----------------------------

def sum_to(n):
    return sum(range(1, n + 1))

def main():
    print(f"sum_to(10) = {sum_to(10)}")
    print(f"sum_to(100) = {sum_to(100)}")


if __name__ == "__main__":
    main()
