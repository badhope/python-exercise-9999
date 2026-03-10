# -----------------------------
# 题目：可变参数*args和**kwargs。
# 描述：使用可变参数创建函数。
# -----------------------------

def func(*args, **kwargs):
    print(f"args: {args}")
    print(f"kwargs: {kwargs}")

def main():
    func(1, 2, 3)
    func(a=1, b=2, c=3)
    func(1, 2, 3, a=4, b=5)


if __name__ == "__main__":
    main()
