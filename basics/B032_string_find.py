# -----------------------------
# 题目：字符串查找和替换。
# 描述：在字符串 "Hello World, World is beautiful" 中查找 "World"，替换所有 "World" 为 "Python"。
# -----------------------------

def main():
    s = "Hello World, World is beautiful"
    print(f"原字符串: {s}")
    print(f"find('World'): {s.find('World')}")
    print(f"count('World'): {s.count('World')}")
    print(f"replace后: {s.replace('World', 'Python')}")


if __name__ == "__main__":
    main()
