# -----------------------------
# 题目：判断字母数字。
# 描述：判断字符串是否只包含字母和数字。
# -----------------------------

def is_alphanumeric(s):
    return s.isalnum()

def main():
    print(f"abc123: {is_alphanumeric('abc123')}")
    print(f"abc 123: {is_alphanumeric('abc 123')}")


if __name__ == "__main__":
    main()
