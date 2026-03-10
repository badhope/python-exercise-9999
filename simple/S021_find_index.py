# -----------------------------
# 题目：查找元素。
# 描述：在列表中查找元素，返回索引。
# -----------------------------

def find_index(lst, target):
    for i, val in enumerate(lst):
        if val == target:
            return i
    return -1

def main():
    print(f"索引: {find_index([1,2,3,4,5], 3)}")


if __name__ == "__main__":
    main()
