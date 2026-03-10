# -----------------------------
# 题目：列表推导式。
# 描述：使用列表推导式生成 1-10 的平方数列表。
# -----------------------------

def main():
    squares = [x**2 for x in range(1, 11)]
    print(f"1-10的平方数: {squares}")
    evens = [x for x in range(1, 21) if x % 2 == 0]
    print(f"1-20的偶数: {evens}")


if __name__ == "__main__":
    main()
