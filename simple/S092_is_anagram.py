# -----------------------------
# 题目：判断字母异位词。
# 描述：判断两个字符串是否为字母异位词。
# -----------------------------

def is_anagram(s1, s2):
    return sorted(s1) == sorted(s2)

def main():
    print(f"anagram和nagaram: {is_anagram('anagram', 'nagaram')}")
    print(f"cat和rat: {is_anagram('cat', 'rat')}")


if __name__ == "__main__":
    main()
