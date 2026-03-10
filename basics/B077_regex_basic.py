# -----------------------------
# 题目：正则表达式基础。
# 描述：使用re模块进行正则匹配。
# -----------------------------

import re

def main():
    text = "My email is test@example.com"
    pattern = r'\w+@\w+\.\w+'
    match = re.search(pattern, text)
    if match:
        print(f"找到: {match.group()}")


if __name__ == "__main__":
    main()
