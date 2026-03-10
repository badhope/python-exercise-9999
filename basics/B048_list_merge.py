# -----------------------------
# 题目：列表合并。
# 描述：合并两个列表 [1,2,3] 和 [4,5,6]。
# -----------------------------

def main():
    lst1 = [1, 2, 3]
    lst2 = [4, 5, 6]
    
    print(f"列表1: {lst1}")
    print(f"列表2: {lst2}")
    print(f"extend: {lst1 + lst2}")
    
    lst3 = lst1.copy()
    lst3.extend(lst2)
    print(f"extend后: {lst3}")


if __name__ == "__main__":
    main()
