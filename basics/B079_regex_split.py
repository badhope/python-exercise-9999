# -----------------------------
# 题目：正则表达式分割。
# 描述：使用re.split进行字符串分割。
# -----------------------------

import re

def main():
    text = "apple,banana;cherry|orange"
    result = re.split(r'[,;|]', text)
    print(f"原字符串: {text}")
    print(f"分割后: {result}")


if __name__ == "__main__":
    main()
