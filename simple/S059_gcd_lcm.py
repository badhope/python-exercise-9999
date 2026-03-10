# -----------------------------
# 题目：最大公约数和最小公倍数。
# 描述：同时求两个数的GCD和LCM。
# -----------------------------

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def lcm(a, b):
    return a * b // gcd(a, b)

def main():
    print(f"12和18: GCD={gcd(12,18)}, LCM={lcm(12,18)}")


if __name__ == "__main__":
    main()
