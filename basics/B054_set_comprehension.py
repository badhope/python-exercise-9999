# -----------------------------
# 题目：集合推导式。
# 描述：使用集合推导式生成集合。
# -----------------------------

def main():
    s = {x**2 for x in range(1, 6)}
    print(f"集合推导式: {s}")
    
    text = "hello world"
    chars = {c for c in text if c.isalpha()}
    print(f"字母集合: {chars}")


if __name__ == "__main__":
    main()
