# -----------------------------
# 题目：列表推导式映射。
# 描述：使用列表推导式对列表元素进行映射。
# -----------------------------

def map_square(lst):
    return [x**2 for x in lst]

def main():
    print(f"平方: {map_square([1,2,3,4,5])}")


if __name__ == "__main__":
    main()
