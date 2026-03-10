# -----------------------------
# 题目：二进制求和。
# 描述：计算两个二进制字符串的和。
# -----------------------------

def add_binary(a, b):
    return bin(int(a, 2) + int(b, 2))[2:]

def main():
    print(f"11+1: {add_binary('11', '1')}")


if __name__ == "__main__":
    main()
