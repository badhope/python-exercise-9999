# -----------------------------
# 题目：map函数练习。
# 描述：使用map函数对列表每个元素进行操作。
# -----------------------------

def main():
    numbers = [1, 2, 3, 4, 5]
    squared = list(map(lambda x: x**2, numbers))
    print(f"原列表: {numbers}")
    print(f"平方: {squared}")
    
    strings = ['1', '2', '3']
    nums = list(map(int, strings))
    print(f"字符串转整数: {nums}")


if __name__ == "__main__":
    main()
