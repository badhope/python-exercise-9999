# -----------------------------
# 题目：数组拆分。
# 描述：将数组分成n对，每对取较小元素，求和最大。
# -----------------------------

def array_pair_sum(nums):
    return sum(sorted(nums)[::2])

def main():
    print(f"最大和: {array_pair_sum([1,4,3,2])}")


if __name__ == "__main__":
    main()
