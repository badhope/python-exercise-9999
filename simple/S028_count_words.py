# -----------------------------
# 题目：单词计数。
# 描述：统计字符串中单词的数量。
# -----------------------------

def count_words(s):
    return len(s.split())

def main():
    print(f"单词数: {count_words('Hello world python')}")


if __name__ == "__main__":
    main()
