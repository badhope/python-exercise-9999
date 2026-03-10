# -----------------------------
# 题目：判断字母。
# 描述：判断字符是否为字母。
# -----------------------------

def is_letter(c):
    return c.isalpha()

def main():
    print(f"a: {is_letter('a')}")
    print(f"1: {is_letter('1')}")


if __name__ == "__main__":
    main()
