# -----------------------------
# 题目：字典按值排序。
# 描述：按字典的值进行排序。
# -----------------------------

def sort_dict_by_value(d):
    return dict(sorted(d.items(), key=lambda x: x[1]))

def main():
    d = {"b": 2, "a": 1, "c": 3}
    print(f"排序后: {sort_dict_by_value(d)}")


if __name__ == "__main__":
    main()
