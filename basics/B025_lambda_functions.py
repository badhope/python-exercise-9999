# -----------------------------
# 题目：lambda匿名函数。
# 描述：使用lambda表达式创建函数，实现加法、排序关键字、map和filter操作。
# -----------------------------

def main():
    add = lambda x, y: x + y
    print(f"add(3, 5) = {add(3, 5)}")
    
    pairs = [(1, 5), (3, 2), (2, 8)]
    pairs_sorted = sorted(pairs, key=lambda x: x[1])
    print(f"按第二个元素排序: {pairs_sorted}")
    
    numbers = [1, 2, 3, 4, 5]
    doubled = list(map(lambda x: x * 2, numbers))
    print(f"map乘2: {doubled}")
    
    evens = list(filter(lambda x: x % 2 == 0, numbers))
    print(f"filter偶数: {evens}")


if __name__ == "__main__":
    main()


# ========== 详细解析 ==========
# lambda：创建匿名函数，语法 lambda 参数: 表达式
# map()：对序列中每个元素应用函数
# filter()：过滤满足条件的元素
# sorted() 的 key 参数：指定排序依据