# -----------------------------
# 题目：字符串连接。
# 描述：将列表中的字符串用分隔符连接。
# -----------------------------

def join_strings(lst, delimiter):
    return delimiter.join(lst)

def main():
    print(f"连接: {join_strings(['a','b','c'], '-')}")


if __name__ == "__main__":
    main()
