# -----------------------------
# 题目：reduce函数练习。
# 描述：使用reduce计算列表元素的累积结果。
# -----------------------------

from functools import reduce

def main():
    numbers = [1, 2, 3, 4, 5]
    product = reduce(lambda x, y: x * y, numbers)
    print(f"列表: {numbers}")
    print(f"累积乘积: {product}")
    
    sum_result = reduce(lambda x, y: x + y, numbers)
    print(f"累积和: {sum_result}")


if __name__ == "__main__":
    main()
