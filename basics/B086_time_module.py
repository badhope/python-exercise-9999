# -----------------------------
# 题目：time模块。
# 描述：使用time模块进行时间操作。
# -----------------------------

import time

def main():
    print(f"当前时间戳: {time.time()}")
    print(f"本地时间: {time.localtime()}")
    time.sleep(0.1)
    print("等待0.1秒完成")


if __name__ == "__main__":
    main()
