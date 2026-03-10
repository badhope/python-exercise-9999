# -----------------------------
# 题目：格式化字符串。
# 描述：使用f-string格式化输出。
# -----------------------------

def format_string(name, age):
    return f"姓名: {name}, 年龄: {age}"

def main():
    print(format_string("张三", 25))


if __name__ == "__main__":
    main()
