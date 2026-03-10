# -----------------------------
# 题目：正则表达式 findall。
# 描述：使用re.findall查找所有匹配项。
# -----------------------------

import re

def main():
    text = "There are 123 numbers 456 in 789 this text"
    numbers = re.findall(r'\d+', text)
    print(f"文本: {text}")
    print(f"数字: {numbers}")


if __name__ == "__main__":
    main()
