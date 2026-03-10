# -----------------------------
# 题目：min和max函数。
# 描述：使用min和max找出列表中的最大最小值。
# -----------------------------

def main():
    nums = [5, 2, 8, 1, 9, 3]
    print(f"列表: {nums}")
    print(f"min: {min(nums)}")
    print(f"max: {max(nums)}")
    print(f"min + max: {min(nums) + max(nums)}")


if __name__ == "__main__":
    main()
