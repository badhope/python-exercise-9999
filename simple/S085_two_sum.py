# -----------------------------
# 题目：两数之和。
# 描述：找出数组中两数之和为目标值的索引。
# -----------------------------

def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []

def main():
    print(f"索引: {two_sum([2,7,11,15], 9)}")


if __name__ == "__main__":
    main()
