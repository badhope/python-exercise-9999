# -----------------------------
# 题目：判断偶数。
# 描述：判断一个数是偶数还是奇数。
# -----------------------------

def is_even(n):
    return n % 2 == 0

def main():
    for i in range(1, 11):
        print(f"{i}: {'偶数' if is_even(i) else '奇数'}")


if __name__ == "__main__":
    main()
