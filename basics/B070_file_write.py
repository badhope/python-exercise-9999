# -----------------------------
# 题目：文件写入。
# 描述：向文件写入内容。
# -----------------------------

def main():
    with open("output.txt", "w") as f:
        f.write("Line 1\n")
        f.write("Line 2\n")
        f.write("Line 3\n")
    print("写入完成")


if __name__ == "__main__":
    main()
