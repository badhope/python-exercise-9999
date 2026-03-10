# -----------------------------
# 题目：统计字符频率。
# 描述：统计字符串中每个字符出现的频率。
# -----------------------------

from collections import Counter

def char_frequency(s):
    return dict(Counter(s))

def main():
    print(f"频率: {char_frequency('hello')}")


if __name__ == "__main__":
    main()
