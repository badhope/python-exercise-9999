# -----------------------------
# 题目：判断质数（优化）。
# 描述：优化判断质数的效率。
# -----------------------------

def is_prime_optimized(n):
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def main():
    primes = [i for i in range(2, 31) if is_prime_optimized(i)]
    print(f"30以内的质数: {primes}")


if __name__ == "__main__":
    main()
