# -----------------------------
# 题目：选择排序。
# 描述：实现选择排序算法。
# -----------------------------

def selection_sort(lst):
    lst = lst.copy()
    n = len(lst)
    for i in range(n):
        min_idx = i
        for j in range(i+1, n):
            if lst[j] < lst[min_idx]:
                min_idx = j
        lst[i], lst[min_idx] = lst[min_idx], lst[i]
    return lst

def main():
    print(f"排序后: {selection_sort([5, 2, 8, 1, 9])}")


if __name__ == "__main__":
    main()
