# -----------------------------
# 题目：字典推导式。
# 描述：使用字典推导式创建 {x: x**2 for x in range(1, 6)}。
# -----------------------------

def main():
    d = {x: x**2 for x in range(1, 6)}
    print(f"字典推导式: {d}")
    
    fruits = ['apple', 'banana', 'cherry']
    d2 = {f: len(f) for f in fruits}
    print(f"水果长度: {d2}")


if __name__ == "__main__":
    main()
