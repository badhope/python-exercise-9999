# -----------------------------
# 题目：函数参数类型（位置参数、默认参数、可变参数）。
# 描述：定义函数 power(base, exp=2)，以及 sum(*args)，调用并测试。
# -----------------------------

def power(base, exp=2):
    return base ** exp


def sum_values(*args):
    total = 0
    for num in args:
        total += num
    return total


def main():
    print(f"power(3) = {power(3)}")
    print(f"power(3, 3) = {power(3, 3)}")
    print(f"sum(1, 2, 3, 4, 5) = {sum_values(1, 2, 3, 4, 5)}")


if __name__ == "__main__":
    main()


# ========== 详细解析 ==========
# 默认参数：在函数定义时给参数赋默认值
# *args：接收任意数量的位置参数，类型为元组
# **kwargs：接收任意数量的关键字参数，类型为字典