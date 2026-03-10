# -----------------------------
# 题目：素数筛选。
# 描述：使用埃拉托斯特尼筛法找出范围内的所有素数。
# -----------------------------

def sieve_of_eratosthenes(n):
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, n+1, i):
                is_prime[j] = False
    return [i for i in range(2, n+1) if is_prime[i]]

def main():
    print(f"50以内的素数: {sieve_of_eratosthenes(50)}")


if __name__ == "__main__":
    main()
