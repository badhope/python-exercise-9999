# -----------------------------
# 题目：颜色分类。
# 描述：对0,1,2三种颜色进行排序。
# -----------------------------

def sort_colors(nums):
    low, mid, high = 0, 0, len(nums) - 1
    while mid <= high:
        if nums[mid] == 0:
            nums[low], nums[mid] = nums[mid], nums[low]
            low += 1
            mid += 1
        elif nums[mid] == 1:
            mid += 1
        else:
            nums[mid], nums[high] = nums[high], nums[mid]
            high -= 1
    return nums

def main():
    print(f"排序后: {sort_colors([2,0,2,1,1,0])}")


if __name__ == "__main__":
    main()
