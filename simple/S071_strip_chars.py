# -----------------------------
# 题目：字符串首尾去字符。
# 描述：去除字符串首尾的指定字符。
# -----------------------------

def strip_chars(s, chars):
    return s.strip(chars)

def main():
    print(f"xxxhelloxxx去x: {strip_chars('xxxhelloxxx', 'x')}")


if __name__ == "__main__":
    main()
