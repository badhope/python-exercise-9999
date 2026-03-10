# -----------------------------
# 题目：二分查找。
# 描述：在有序列表中查找元素。
# -----------------------------

def binary_search(lst, target):
    left, right = 0, len(lst) - 1
    while left <= right:
        mid = (left + right) // 2
        if lst[mid] == target:
            return mid
        elif lst[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

def main():
    lst = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    print(f"索引: {binary_search(lst, 5)}")


if __name__ == "__main__":
    main()
