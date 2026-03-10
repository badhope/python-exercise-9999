# -----------------------------
# 题目：合并两个有序数组。
# 描述：将两个有序数组合并为一个有序数组。
# -----------------------------

def merge_sorted_arrays(nums1, nums2):
    return sorted(nums1 + nums2)

def main():
    print(f"合并: {merge_sorted_arrays([1,3,5], [2,4,6])}")


if __name__ == "__main__":
    main()
