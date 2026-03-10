# -----------------------------
# 题目：子集II。
# 描述：生成有重复元素的子集。
# -----------------------------

def subsets_with_dup(nums):
    nums.sort()
    result = [[]]
    start = 0
    for i in range(len(nums)):
        if i == 0 or nums[i] != nums[i-1]:
            start = 0
        size = len(result)
        for j in range(start, size):
            result.append(result[j] + [nums[i]])
        start = size
    return result

def main():
    print(f"子集: {subsets_with_dup([1,2,2])}")


if __name__ == "__main__":
    main()
