# -----------------------------
# 题目：字符串分割。
# 描述：按指定分隔符分割字符串。
# -----------------------------

def split_string(s, delimiter):
    return s.split(delimiter)

def main():
    print(f"a,b,c按逗号分割: {split_string('a,b,c', ',')}")


if __name__ == "__main__":
    main()
