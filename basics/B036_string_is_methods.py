# -----------------------------
# 题目：判断字符串类型。
# 描述：判断字符串 "123abc", "ABC", "123", "   " 分别是数字、字母、大小写哪种类型。
# -----------------------------

def main():
    tests = ["123abc", "ABC", "123", "   ", "Hello123"]
    for s in tests:
        print(f"'{s}': isdigit={s.isdigit()}, isalpha={s.isalpha()}, isalnum={s.isalnum()}, isspace={s.isspace()}")


if __name__ == "__main__":
    main()
