# -----------------------------
# 题目：数字各位求和。
# 描述：计算一个数字各位数字之和。
# -----------------------------

def sum_digits(n):
    return sum(int(d) for d in str(abs(n)))

def main():
    print(f"12345各位和: {sum_digits(12345)}")


if __name__ == "__main__":
    main()
