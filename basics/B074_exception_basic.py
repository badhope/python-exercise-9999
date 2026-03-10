# -----------------------------
# 题目：异常处理try-except。
# 描述：捕获和处理不同类型的异常。
# -----------------------------

def main():
    try:
        result = 10 / 0
    except ZeroDivisionError:
        print("不能除以零")
    
    try:
        num = int("abc")
    except ValueError:
        print("无效的数字格式")


if __name__ == "__main__":
    main()
