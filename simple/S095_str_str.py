# -----------------------------
# 题目：实现strStr。
# 描述：实现字符串查找函数。
# -----------------------------

def str_str(haystack, needle):
    return haystack.find(needle)

def main():
    print(f"索引: {str_str('hello', 'll')}")


if __name__ == "__main__":
    main()
