# -----------------------------
# 题目：取余运算。
# 描述：给定两个数，返回它们的余数。
# -----------------------------

def modulo_two_numbers(a, b):
    if b == 0:
        return "错误：除数不能为0"
    return a % b

def main():
    print(f"10 % 3 = {modulo_two_numbers(10, 3)}")
    print(f"15 % 4 = {modulo_two_numbers(15, 4)}")


if __name__ == "__main__":
    main()
