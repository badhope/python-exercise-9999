# -----------------------------
# 题目：判断回文数。
# 描述：判断一个数是否是回文数。
# -----------------------------

def is_palindrome_num(n):
    s = str(n)
    return s == s[::-1]

def main():
    for i in [121, 123, 12321, -121]:
        print(f"{i}: {is_palindrome_num(i)}")


if __name__ == "__main__":
    main()
