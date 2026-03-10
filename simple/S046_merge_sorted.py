# -----------------------------
# 题目：合并两个有序列表。
# 描述：将两个有序列表合并为一个有序列表。
# -----------------------------

def merge_sorted_lists(lst1, lst2):
    result = []
    i = j = 0
    while i < len(lst1) and j < len(lst2):
        if lst1[i] <= lst2[j]:
            result.append(lst1[i])
            i += 1
        else:
            result.append(lst2[j])
            j += 1
    result.extend(lst1[i:])
    result.extend(lst2[j:])
    return result

def main():
    print(f"合并: {merge_sorted_lists([1,3,5], [2,4,6])}")


if __name__ == "__main__":
    main()
