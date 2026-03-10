# -----------------------------
# 题目：正则表达式替换。
# 描述：使用re.sub进行字符串替换。
# -----------------------------

import re

def main():
    text = "Hello World World"
    result = re.sub(r'World', 'Python', text)
    print(f"原字符串: {text}")
    print(f"替换后: {result}")


if __name__ == "__main__":
    main()
