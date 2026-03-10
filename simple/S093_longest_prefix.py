# -----------------------------
# 题目：最长公共前缀。
# 找出字符串数组的最长公共前缀。
# -----------------------------

def longest_common_prefix(strs):
    if not strs:
        return ""
    prefix = strs[0]
    for s in strs[1:]:
        while not s.startswith(prefix):
            prefix = prefix[:-1]
            if not prefix:
                return ""
    return prefix

def main():
    print(f"前缀: {longest_common_prefix(['flower','flow','flight'])}")


if __name__ == "__main__":
    main()
