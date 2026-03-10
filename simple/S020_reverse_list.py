# -----------------------------
# 题目：反转列表。
# 描述：反转列表的顺序（不使用reverse）。
# -----------------------------

def reverse_list(lst):
    return lst[::-1]

def main():
    print(f"反转[1,2,3,4,5]: {reverse_list([1,2,3,4,5])}")


if __name__ == "__main__":
    main()
