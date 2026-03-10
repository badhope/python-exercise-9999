# -----------------------------
# 题目：pow(x, n)。
# 描述：实现x的n次幂函数。
# -----------------------------

def my_pow(x, n):
    if n < 0:
        x = 1 / x
        n = -n
    result = 1
    while n:
        if n & 1:
            result *= x
        x *= x
        n >>= 1
    return result

def main():
    print(f"2^10: {my_pow(2, 10)}")


if __name__ == "__main__":
    main()
