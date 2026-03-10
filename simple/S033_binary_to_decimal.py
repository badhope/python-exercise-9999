# -----------------------------
# 题目：二进制转十进制。
# 描述：将二进制数转换为十进制。
# -----------------------------

def to_decimal(binary):
    return int(binary, 2)

def main():
    print(f"1010的十进制: {to_decimal('1010')}")
    print(f"11111111的十进制: {to_decimal('11111111')}")


if __name__ == "__main__":
    main()
