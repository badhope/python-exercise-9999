# -----------------------------
# 题目：判断完全数。
# 描述：判断一个数是否为完全数（所有因子之和等于本身）。
# -----------------------------

def is_perfect(n):
    if n <= 1:
        return False
    divisors = [i for i in range(1, n) if n % i == 0]
    return sum(divisors) == n

def main():
    for i in [6, 28, 496, 12]:
        print(f"{i}: {'是完全数' if is_perfect(i) else '不是完全数'}")


if __name__ == "__main__":
    main()
