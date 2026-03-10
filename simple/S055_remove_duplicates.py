# -----------------------------
# 题目：删除重复字符。
# 描述：删除字符串中的重复字符，保持顺序。
# -----------------------------

def remove_duplicates(s):
    seen = set()
    result = []
    for c in s:
        if c not in seen:
            seen.add(c)
            result.append(c)
    return "".join(result)

def main():
    print(f"删除重复: {remove_duplicates('banana')}")


if __name__ == "__main__":
    main()
