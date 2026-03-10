# -----------------------------
# 题目：搜索插入位置。
# 描述：找到目标值应该插入的位置。
# -----------------------------

def search_insert(nums, target):
    for i, num in enumerate(nums):
        if num >= target:
            return i
    return len(nums)

def main():
    print(f"插入位置: {search_insert([1,3,5,6], 5)}")


if __name__ == "__main__":
    main()
