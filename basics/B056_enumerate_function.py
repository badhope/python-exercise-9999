# -----------------------------
# 题目：enumerate函数练习。
# 描述：使用enumerate获取列表的索引和值。
# -----------------------------

def main():
    fruits = ['apple', 'banana', 'cherry']
    for i, fruit in enumerate(fruits):
        print(f"{i}: {fruit}")
    
    print(f"enumerate: {list(enumerate(fruits))}")


if __name__ == "__main__":
    main()
