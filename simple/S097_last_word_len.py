# -----------------------------
# 题目：最后一个单词的长度。
# 描述：计算字符串中最后一个单词的长度。
# -----------------------------

def length_of_last_word(s):
    words = s.split()
    return len(words[-1]) if words else 0

def main():
    print(f"长度: {length_of_last_word('Hello World')}")


if __name__ == "__main__":
    main()
