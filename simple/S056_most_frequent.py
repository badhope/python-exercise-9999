# -----------------------------
# 题目：列表中出现次数最多的元素。
# 描述：找出列表中出现次数最多的元素。
# -----------------------------

from collections import Counter

def most_frequent(lst):
    if not lst:
        return None
    counter = Counter(lst)
    return counter.most_common(1)[0][0]

def main():
    print(f"最多: {most_frequent([1,2,2,3,3,3])}")


if __name__ == "__main__":
    main()
