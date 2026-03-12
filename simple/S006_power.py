# -----------------------------
# 题目：幂运算。
# 描述：计算一个数的n次幂。
# -----------------------------

def power(base, exponent):
    return base ** exponent

def main():
    print(f"2^3 = {power(2, 3)}")
    print(f"5^2 = {power(5, 2)}")
    print(f"3^4 = {power(3, 4)}")


if __name__ == "__main__":
    main()
