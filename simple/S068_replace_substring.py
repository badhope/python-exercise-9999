# -----------------------------
# 题目：字符串替换。
# 描述：将字符串中的指定子串替换。
# -----------------------------

def replace_substring(s, old, new):
    return s.replace(old, new)

def main():
    print(f"hello中l替换为x: {replace_substring('hello', 'l', 'x')}")


if __name__ == "__main__":
    main()
