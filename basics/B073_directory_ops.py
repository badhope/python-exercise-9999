# -----------------------------
# 题目：目录操作。
# 描述：列出目录内容，创建目录。
# -----------------------------

import os

def main():
    print(f"当前目录: {os.getcwd()}")
    print(f"目录内容: {os.listdir('.')}")
    print(f"是否存在文件: {os.path.exists('test.txt')}")


if __name__ == "__main__":
    main()
