# -----------------------------
# 题目：os模块。
# 描述：使用os模块进行系统操作。
# -----------------------------

import os

def main():
    print(f"系统: {os.name}")
    print(f"环境变量: {os.getenv('PATH', 'N/A')[:50]}...")
    print(f"当前目录: {os.getcwd()}")


if __name__ == "__main__":
    main()
