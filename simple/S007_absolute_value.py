# -----------------------------
# 题目：绝对值。
# 描述：计算一个数的绝对值。
# -----------------------------

def absolute_value(n):
    if n < 0:
        return -n
    return n

def main():
    print(f"|-5| = {absolute_value(-5)}")
    print(f"|3| = {absolute_value(3)}")
    print(f"|0| = {absolute_value(0)}")


if __name__ == "__main__":
    main()
