# -----------------------------
# 题目：判断素数。
# 描述：编写函数判断一个数是否为素数。
# -----------------------------

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def main():
    for i in range(1, 21):
        print(f"{i}: {'是素数' if is_prime(i) else '不是素数'}")


if __name__ == "__main__":
    main()
