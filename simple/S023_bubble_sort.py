# -----------------------------
# 题目：冒泡排序。
# 描述：实现冒泡排序算法。
# -----------------------------

def bubble_sort(lst):
    lst = lst.copy()
    n = len(lst)
    for i in range(n):
        for j in range(0, n-i-1):
            if lst[j] > lst[j+1]:
                lst[j], lst[j+1] = lst[j+1], lst[j]
    return lst

def main():
    print(f"排序后: {bubble_sort([5, 2, 8, 1, 9])}")


if __name__ == "__main__":
    main()
