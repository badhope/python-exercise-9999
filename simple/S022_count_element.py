# -----------------------------
# 题目：计数元素。
# 描述：统计列表中某个元素出现的次数。
# -----------------------------

def count_element(lst, target):
    return lst.count(target)

def main():
    print(f"次数: {count_element([1,2,2,3,2,4], 2)}")


if __name__ == "__main__":
    main()
