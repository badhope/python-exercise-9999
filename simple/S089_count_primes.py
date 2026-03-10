# -----------------------------
# 题目：计数质数。
# 描述：统计n以内质数的数量。
# -----------------------------

def count_primes(n):
    if n < 2:
        return 0
    is_prime = [True] * n
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, n, i):
                is_prime[j] = False
    return sum(is_prime)

def main():
    print(f"20以内质数数量: {count_primes(20)}")


if __name__ == "__main__":
    main()
