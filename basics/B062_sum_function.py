# -----------------------------
# 题目：sum函数。
# 描述：使用sum计算列表元素总和。
# -----------------------------

def main():
    nums = [1, 2, 3, 4, 5]
    print(f"列表: {nums}")
    print(f"sum: {sum(nums)}")
    print(f"sum with start: {sum(nums, 10)}")


if __name__ == "__main__":
    main()
