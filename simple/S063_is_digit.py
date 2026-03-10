# -----------------------------
# 题目：判断数字。
# 描述：判断字符串是否为数字。
# -----------------------------

def is_digit(s):
    return s.isdigit()

def main():
    print(f"123: {is_digit('123')}")
    print(f"12a: {is_digit('12a')}")


if __name__ == "__main__":
    main()
