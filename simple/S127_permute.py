# -----------------------------
# 题目：全排列。
# 描述：生成数组的全排列。
# -----------------------------

def permute(nums):
    result = []
    def backtrack(start):
        if start == len(nums):
            result.append(nums[:])
        for i in range(start, len(nums)):
            nums[start], nums[i] = nums[i], nums[start]
            backtrack(start + 1)
            nums[start], nums[i] = nums[i], nums[start]
    backtrack(0)
    return result

def main():
    print(f"全排列: {permute([1,2,3])}")


if __name__ == "__main__":
    main()
