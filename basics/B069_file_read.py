# -----------------------------
# 题目：文件读取。
# 描述：读取文件内容并打印。
# -----------------------------

def main():
    try:
        with open("test.txt", "w") as f:
            f.write("Hello\nWorld")
        
        with open("test.txt", "r") as f:
            content = f.read()
            print(f"文件内容: {content}")
    except FileNotFoundError:
        print("文件不存在")


if __name__ == "__main__":
    main()
