# -----------------------------
# 题目：字符串开头判断。
# 描述：判断字符串是否以指定前缀开头。
# -----------------------------

def starts_with(s, prefix):
    return s.startswith(prefix)

def main():
    print(f"hello以hel开头: {starts_with('hello', 'hel')}")


if __name__ == "__main__":
    main()
