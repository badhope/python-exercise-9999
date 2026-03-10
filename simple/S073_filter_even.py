# -----------------------------
# 题目：列表推导式过滤。
# 描述：使用列表推导式过滤列表元素。
# -----------------------------

def filter_even(lst):
    return [x for x in lst if x % 2 == 0]

def main():
    print(f"过滤偶数: {filter_even([1,2,3,4,5,6,7,8])}")


if __name__ == "__main__":
    main()
