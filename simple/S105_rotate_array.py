# -----------------------------
# 题目：旋转数组。
# 描述：将数组中的元素向右轮转k个位置。
# -----------------------------

def rotate_array(nums, k):
    k = k % len(nums)
    nums[:] = nums[-k:] + nums[:-k]

def main():
    nums = [1,2,3,4,5,6,7]
    rotate_array(nums, 3)
    print(f"旋转后: {nums}")


if __name__ == "__main__":
    main()
