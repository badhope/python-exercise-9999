# -----------------------------
# 题目：去重列表。
# 描述：去除列表中的重复元素。
# -----------------------------

def unique_list(lst):
    return list(set(lst))

def main():
    print(f"去重: {unique_list([1,2,2,3,3,4])}")


if __name__ == "__main__":
    main()
