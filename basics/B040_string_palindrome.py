# -----------------------------
# 题目：字符串翻转和回文判断。
# 描述：判断字符串 "racecar" 和 "hello" 是否是回文。
# -----------------------------

def is_palindrome(s):
    return s == s[::-1]

def main():
    tests = ["racecar", "hello", "level", "world"]
    for s in tests:
        result = is_palindrome(s)
        print(f"'{s}' 是回文: {result}")


if __name__ == "__main__":
    main()
