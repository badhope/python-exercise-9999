# -----------------------------
# 题目：字符串统计。
# 描述：统计字符串 "hello world" 中每个字符出现的次数。
# -----------------------------

from collections import Counter

def main():
    s = "hello world"
    counter = Counter(s)
    print(f"字符串: '{s}'")
    print(f"字符统计: {dict(counter)}")
    print(f"最常见的3个字符: {counter.most_common(3)}")


if __name__ == "__main__":
    main()
