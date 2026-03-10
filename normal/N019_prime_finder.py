# -----------------------------
# 题目：素数判断。
# 描述：判断一个数是否为素数，并找出范围内的所有素数。
# -----------------------------

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def find_primes_in_range(start, end):
    return [n for n in range(start, end + 1) if is_prime(n)]

def main():
    print(f"100以内的素数: {find_primes_in_range(1, 100)}")


if __name__ == "__main__":
    main()
