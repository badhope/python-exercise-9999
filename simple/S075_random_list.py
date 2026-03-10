# -----------------------------
# 题目：生成随机数列表。
# 描述：生成指定长度的随机数列表。
# -----------------------------

import random

def random_list(length, start=1, end=100):
    return [random.randint(start, end) for _ in range(length)]

def main():
    print(f"随机列表: {random_list(10)}")


if __name__ == "__main__":
    main()
