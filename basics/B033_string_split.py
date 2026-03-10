# -----------------------------
# 题目：字符串分割和连接。
# 描述：将字符串 "apple,banana,cherry" 用逗号分割，然后使用 "-" 连接。
# -----------------------------

def main():
    s = "apple,banana,cherry"
    parts = s.split(",")
    print(f"分割后: {parts}")
    print(f"用-连接: {'-'.join(parts)}")


if __name__ == "__main__":
    main()
