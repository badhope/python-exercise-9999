# -----------------------------
# 题目：删除空格。
# 描述：删除字符串中的所有空格。
# -----------------------------

def remove_spaces(s):
    return s.replace(" ", "")

def main():
    print(f"删除空格: {remove_spaces('h e l l o')}")


if __name__ == "__main__":
    main()
