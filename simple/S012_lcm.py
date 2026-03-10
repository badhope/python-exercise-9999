# -----------------------------
# 题目：求最小公倍数。
# 描述：求两个数的最小公倍数。
# -----------------------------

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def lcm(a, b):
    return a * b // gcd(a, b)

def main():
    print(f"lcm(4, 6) = {lcm(4, 6)}")
    print(f"lcm(5, 7) = {lcm(5, 7)}")


if __name__ == "__main__":
    main()
