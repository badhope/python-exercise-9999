# -----------------------------
# 题目：判断质数函数。
# 描述：实现一个判断质数的函数。
# -----------------------------

def is_prime_simple(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True

def main():
    primes = [i for i in range(1, 21) if is_prime_simple(i)]
    print(f"20以内的质数: {primes}")


if __name__ == "__main__":
    main()
