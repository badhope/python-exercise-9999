# -----------------------------
# 题目：找出列表交集。
# 描述：找出两个列表的交集。
# -----------------------------

def list_intersection(lst1, lst2):
    return list(set(lst1) & set(lst2))

def main():
    print(f"交集: {list_intersection([1,2,3,4], [3,4,5,6])}")


if __name__ == "__main__":
    main()
