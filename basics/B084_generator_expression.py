# -----------------------------
# 题目：生成器表达式。
# 描述：使用生成器表达式代替列表推导式。
# -----------------------------

def main():
    gen = (x**2 for x in range(1, 6))
    print(f"生成器: {list(gen)}")
    
    for num in (x for x in range(5)):
        print(num)


if __name__ == "__main__":
    main()
