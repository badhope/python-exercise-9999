# -----------------------------
# 题目：字符串结尾判断。
# 描述：判断字符串是否以指定后缀结尾。
# -----------------------------

def ends_with(s, suffix):
    return s.endswith(suffix)

def main():
    print(f"hello以llo结尾: {ends_with('hello', 'llo')}")


if __name__ == "__main__":
    main()
