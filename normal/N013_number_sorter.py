# -----------------------------
# 题目：数字排序。
# 描述：对用户输入的数字进行升序和降序排序。
# -----------------------------

def sort_numbers_ascending(numbers):
    return sorted(numbers)

def sort_numbers_descending(numbers):
    return sorted(numbers, reverse=True)

def main():
    numbers = [5, 2, 8, 1, 9, 3]
    print(f"原数组: {numbers}")
    print(f"升序: {sort_numbers_ascending(numbers)}")
    print(f"降序: {sort_numbers_descending(numbers)}")


if __name__ == "__main__":
    main()
