# -----------------------------
# 题目：找出重复的数字。
# 描述：找出数组中重复的数字。
# -----------------------------

def find_duplicate(nums):
    seen = set()
    for num in nums:
        if num in seen:
            return num
        seen.add(num)
    return None

def main():
    print(f"重复: {find_duplicate([1,2,3,2,4])}")


if __name__ == "__main__":
    main()
