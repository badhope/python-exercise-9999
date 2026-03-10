# -----------------------------
# 题目：十进制转二进制。
# 描述：将十进制数转换为二进制。
# -----------------------------

def to_binary(n):
    return bin(n)[2:]

def main():
    print(f"10的二进制: {to_binary(10)}")
    print(f"255的二进制: {to_binary(255)}")


if __name__ == "__main__":
    main()
