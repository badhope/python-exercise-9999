# -----------------------------
# 题目：最大公约数（递归）。
# 描述：使用递归实现欧几里得算法。
# -----------------------------

def gcd_recursive(a, b):
    if b == 0:
        return a
    return gcd_recursive(b, a % b)

def main():
    print(f"gcd(48, 18) = {gcd_recursive(48, 18)}")


if __name__ == "__main__":
    main()
