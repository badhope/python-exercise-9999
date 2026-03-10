# -----------------------------
# 题目：反转字符串。
# 描述：原地反转字符串。
# -----------------------------

def reverse_string(s):
    s[:] = s[::-1]

def main():
    s = ["h","e","l","l","o"]
    reverse_string(s)
    print(f"反转后: {s}")


if __name__ == "__main__":
    main()
