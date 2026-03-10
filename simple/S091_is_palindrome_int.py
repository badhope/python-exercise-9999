# -----------------------------
# 题目：回文数判断。
# 描述：判断一个整数是否为回文数。
# -----------------------------

def is_palindrome_int(x):
    if x < 0:
        return False
    return str(x) == str(x)[::-1]

def main():
    print(f"121: {is_palindrome_int(121)}")
    print(f"-121: {is_palindrome_int(-121)}")


if __name__ == "__main__":
    main()
