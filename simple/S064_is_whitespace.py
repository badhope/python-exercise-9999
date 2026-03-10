# -----------------------------
# 题目：判断空格。
# 描述：判断字符是否为空格。
# -----------------------------

def is_whitespace(c):
    return c.isspace()

def main():
    print(f"' ': {is_whitespace(' ')}")
    print(f"'a': {is_whitespace('a')}")


if __name__ == "__main__":
    main()
