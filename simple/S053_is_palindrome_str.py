# -----------------------------
# 题目：回文串判断。
# 描述：判断字符串是否为回文串。
# -----------------------------

def is_palindrome_string(s):
    s = s.lower().replace(" ", "")
    return s == s[::-1]

def main():
    print(f"racecar: {is_palindrome_string('racecar')}")
    print(f"hello: {is_palindrome_string('hello')}")


if __name__ == "__main__":
    main()
