# -----------------------------
# 题目：最大值和最小值。
# 描述：找出列表中的最大值和最小值（不使用max/min）。
# -----------------------------

def find_max_min(lst):
    return max(lst), min(lst)

def main():
    nums = [5, 2, 8, 1, 9, 3]
    max_val, min_val = find_max_min(nums)
    print(f"列表: {nums}")
    print(f"最大值: {max_val}, 最小值: {min_val}")


if __name__ == "__main__":
    main()
