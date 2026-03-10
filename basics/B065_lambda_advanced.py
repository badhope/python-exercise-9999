# -----------------------------
# 题目：匿名函数综合练习。
# 描述：使用匿名函数实现各种功能。
# -----------------------------

def main():
    pairs = [(1, 5), (3, 2), (2, 8)]
    print(f"按和排序: {sorted(pairs, key=lambda x: x[0] + x[1])}")
    
    add = lambda x, y: x + y
    print(f"add(3,4): {add(3, 4)}")


if __name__ == "__main__":
    main()
