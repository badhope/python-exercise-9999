# -----------------------------
# 题目：字符串去除空白字符。
# 描述：去除字符串 "  hello   world  " 两端和中间的多余空格。
# -----------------------------

def main():
    s = "  hello   world  "
    print(f"原字符串: '{s}'")
    print(f"strip(): '{s.strip()}'")
    print(f"lstrip(): '{s.lstrip()}'")
    print(f"rstrip(): '{s.rstrip()}'")
    print(f"replace后: '{s.replace(' ', '')}'")


if __name__ == "__main__":
    main()
