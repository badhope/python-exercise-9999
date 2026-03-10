# -----------------------------
# 题目：列表元素求和。
# 描述：对列表中的所有元素求和。
# -----------------------------

def list_sum(lst):
    total = 0
    for num in lst:
        total += num
    return total

def main():
    print(f"sum([1,2,3,4,5]) = {list_sum([1,2,3,4,5])}")


if __name__ == "__main__":
    main()
