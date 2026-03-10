# -----------------------------
# 题目：字符串查找。
# 描述：查找子串首次出现的索引。
# -----------------------------

def find_substring(s, sub):
    return s.find(sub)

def main():
    print(f"hello中ll的索引: {find_substring('hello', 'll')}")


if __name__ == "__main__":
    main()
