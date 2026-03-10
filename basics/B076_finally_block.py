# -----------------------------
# 题目：finally语句。
# 描述：使用finally确保代码始终执行。
# -----------------------------

def main():
    try:
        f = open("test.txt", "r")
        content = f.read()
    except FileNotFoundError:
        print("文件不存在")
    finally:
        print("执行清理操作")


if __name__ == "__main__":
    main()
