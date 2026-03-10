# -----------------------------
# 题目：只出现一次的数字。
# 描述：找出数组中只出现一次的数字，其他数字都出现两次。
# -----------------------------

def single_number(nums):
    result = 0
    for num in nums:
        result ^= num
    return result

def main():
    print(f"单独数字: {single_number([2,2,1])}")


if __name__ == "__main__":
    main()
