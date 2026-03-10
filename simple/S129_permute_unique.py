# -----------------------------
# 题目：全排列II。
# 描述：生成有重复元素的全排列。
# -----------------------------

def permute_unique(nums):
    nums.sort()
    result = []
    used = [False] * len(nums)
    def backtrack(path):
        if len(path) == len(nums):
            result.append(path[:])
            return
        for i in range(len(nums)):
            if used[i] or (i > 0 and nums[i] == nums[i-1] and not used[i-1]):
                continue
            used[i] = True
            path.append(nums[i])
            backtrack(path)
            path.pop()
            used[i] = False
    backtrack([])
    return result

def main():
    print(f"全排列: {permute_unique([1,1,2])}")


if __name__ == "__main__":
    main()
