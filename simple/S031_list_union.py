# -----------------------------
# 题目：找出列表并集。
# 描述：找出两个列表的并集。
# -----------------------------

def list_union(lst1, lst2):
    return list(set(lst1) | set(lst2))

def main():
    print(f"并集: {list_union([1,2,3,4], [3,4,5,6])}")


if __name__ == "__main__":
    main()
