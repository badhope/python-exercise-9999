# -----------------------------
# 题目：九九乘法表。
# 描述：打印九九乘法表。
# -----------------------------

def print_multiplication_table():
    for i in range(1, 10):
        for j in range(1, i + 1):
            print(f"{j}*{i}={i*j:2d}", end="  ")
        print()

def main():
    print("=== 九九乘法表 ===")
    print_multiplication_table()


if __name__ == "__main__":
    main()
