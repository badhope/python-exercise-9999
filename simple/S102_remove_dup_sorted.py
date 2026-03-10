# -----------------------------
# 题目：删除排序数组中的重复项。
# 描述：删除有序数组中的重复项，返回新长度。
# -----------------------------

def remove_duplicates_sorted(nums):
    if not nums:
        return 0
    slow = 0
    for fast in range(1, len(nums)):
        if nums[fast] != nums[slow]:
            slow += 1
            nums[slow] = nums[fast]
    return slow + 1

def main():
    nums = [1,1,2]
    print(f"新长度: {remove_duplicates_sorted(nums)}")


if __name__ == "__main__":
    main()
