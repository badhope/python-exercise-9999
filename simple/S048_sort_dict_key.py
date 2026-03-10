# -----------------------------
# 题目：字典按键排序。
# 描述：按字典的键进行排序。
# -----------------------------

def sort_dict_by_key(d):
    return dict(sorted(d.items()))

def main():
    d = {"b": 2, "a": 1, "c": 3}
    print(f"排序后: {sort_dict_by_key(d)}")


if __name__ == "__main__":
    main()
