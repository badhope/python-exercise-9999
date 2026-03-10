# -----------------------------
# 题目：字符串大小写转换。
# 描述：将字符串 "Hello World" 转换为全大写、全小写、首字母大写。
# -----------------------------

def main():
    s = "Hello World"
    print(f"原字符串: {s}")
    print(f"upper(): {s.upper()}")
    print(f"lower(): {s.lower()}")
    print(f"title(): {s.title()}")
    print(f"capitalize(): {s.capitalize()}")


if __name__ == "__main__":
    main()
