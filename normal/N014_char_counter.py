# -----------------------------
# 题目：统计字数。
# 描述：统计字符串中的字母、数字、空格和其他字符数量。
# -----------------------------

def count_char_types(s):
    letters = digits = spaces = other = 0
    for c in s:
        if c.isalpha():
            letters += 1
        elif c.isdigit():
            digits += 1
        elif c.isspace():
            spaces += 1
        else:
            other += 1
    return letters, digits, spaces, other

def main():
    s = "Hello World 123!"
    letters, digits, spaces, other = count_char_types(s)
    print(f"字符串: '{s}'")
    print(f"字母: {letters}, 数字: {digits}, 空格: {spaces}, 其他: {other}")


if __name__ == "__main__":
    main()
