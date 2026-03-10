# -----------------------------
# 题目：字典操作。
# 描述：创建字典并练习 get、keys、values、items 方法。
# -----------------------------

def main():
    d = {'name': 'Alice', 'age': 25, 'city': 'Beijing'}
    print(f"字典: {d}")
    print(f"get('name'): {d.get('name')}")
    print(f"keys: {list(d.keys())}")
    print(f"values: {list(d.values())}")
    print(f"items: {list(d.items())}")


if __name__ == "__main__":
    main()
