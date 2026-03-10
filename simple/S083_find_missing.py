# -----------------------------
# 题目：找出缺失的数字。
# 描述：在0到n的序列中找出缺失的数字。
# -----------------------------

def find_missing(nums, n):
    expected_sum = n * (n + 1) // 2
    return expected_sum - sum(nums)

def main():
    print(f"缺失: {find_missing([0,1,3,4], 4)}")


if __name__ == "__main__":
    main()
