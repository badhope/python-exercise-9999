# -----------------------------
# 题目：找最大值和最小值。
# 描述：在列表中找出最大值和最小值，不使用内置函数。
# -----------------------------

def find_max_min(numbers):
    if not numbers:
        return None, None
    max_val = min_val = numbers[0]
    for num in numbers[1:]:
        if num > max_val:
            max_val = num
        if num < min_val:
            min_val = num
    return max_val, min_val

def main():
    numbers = [5, 2, 8, 1, 9, 3, 7]
    max_val, min_val = find_max_min(numbers)
    print(f"数组: {numbers}")
    print(f"最大值: {max_val}, 最小值: {min_val}")


if __name__ == "__main__":
    main()
