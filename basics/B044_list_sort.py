# -----------------------------
# 题目：列表排序。
# 描述：对列表 [5,2,8,1,9] 进行排序（升序和降序）。
# -----------------------------

def main():
    lst = [5, 2, 8, 1, 9]
    print(f"原列表: {lst}")
    
    lst_sorted = sorted(lst)
    print(f"升序: {lst_sorted}")
    
    lst_sorted_desc = sorted(lst, reverse=True)
    print(f"降序: {lst_sorted_desc}")
    
    lst_copy = lst.copy()
    lst_copy.sort()
    print(f"原地排序: {lst_copy}")


if __name__ == "__main__":
    main()
