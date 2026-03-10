# -----------------------------
# 题目：求众数。
# 描述：找出数组中出现次数超过一半的元素。
# -----------------------------

def majority_element(nums):
    counts = {}
    for num in nums:
        counts[num] = counts.get(num, 0) + 1
    for num, count in counts.items():
        if count > len(nums) // 2:
            return num
    return None

def main():
    print(f"众数: {majority_element([3,2,3])}")


if __name__ == "__main__":
    main()
