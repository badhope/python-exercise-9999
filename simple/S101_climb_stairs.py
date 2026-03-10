# -----------------------------
# 题目：爬楼梯。
# 描述：爬n阶楼梯，每次爬1或2步，有多少种方法。
# -----------------------------

def climb_stairs(n):
    if n <= 2:
        return n
    a, b = 1, 2
    for _ in range(3, n + 1):
        a, b = b, a + b
    return b

def main():
    print(f"5阶楼梯方法数: {climb_stairs(5)}")


if __name__ == "__main__":
    main()
