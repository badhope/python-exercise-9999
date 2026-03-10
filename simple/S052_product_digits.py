# -----------------------------
# 题目：数字各位求乘积。
# 描述：计算一个数字各位数字之积。
# -----------------------------

def product_digits(n):
    result = 1
    for d in str(abs(n)):
        result *= int(d)
    return result

def main():
    print(f"123各位积: {product_digits(123)}")


if __name__ == "__main__":
    main()
