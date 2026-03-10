# -----------------------------
# 题目：字典合并。
# 描述：合并两个字典 dict1 = {'a': 1, 'b': 2} 和 dict2 = {'b': 3, 'c': 4}。
# -----------------------------

def main():
    dict1 = {'a': 1, 'b': 2}
    dict2 = {'b': 3, 'c': 4}
    
    merged = {**dict1, **dict2}
    print(f"合并后: {merged}")
    
    dict1.update(dict2)
    print(f"update后: {dict1}")


if __name__ == "__main__":
    main()
