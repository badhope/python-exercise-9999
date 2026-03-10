# -----------------------------
# 题目：random模块。
# 描述：使用random模块生成随机数。
# -----------------------------

import random

def main():
    print(f"randint: {random.randint(1, 100)}")
    print(f"random: {random.random()}")
    print(f"choice: {random.choice(['a', 'b', 'c'])}")
    print(f"shuffle: {random.sample([1,2,3,4,5], 3)}")


if __name__ == "__main__":
    main()
