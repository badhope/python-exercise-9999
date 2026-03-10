# -----------------------------
# 题目：存在重复元素。
# 描述：判断数组中是否存在重复元素。
# -----------------------------

def contains_duplicate(nums):
    return len(nums) != len(set(nums))

def main():
    print(f"有重复: {contains_duplicate([1,2,3,1])}")


if __name__ == "__main__":
    main()
