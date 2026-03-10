# -----------------------------
# 题目：子集。
# 描述：生成数组的所有子集。
# -----------------------------

def subsets(nums):
    result = [[]]
    for num in nums:
        result += [curr + [num] for curr in result]
    return result

def main():
    print(f"子集: {subsets([1,2,3])}")


if __name__ == "__main__":
    main()
