# -----------------------------
# 题目：两数之商。
# 描述：给定两个数，返回它们的商。
# -----------------------------

def divide_two_numbers(a, b):
    if b == 0:
        return "错误：除数不能为0"
    return a / b

def main():
    print(f"10 / 2 = {divide_two_numbers(10, 2)}")
    print(f"7 / 3 = {divide_two_numbers(7, 3):.2f}")


if __name__ == "__main__":
    main()
