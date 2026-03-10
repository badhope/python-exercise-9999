# -----------------------------
# 题目：函数返回值（多个返回值）。
# 描述：定义函数 calculate(a, b)，返回和、差、积、商四个结果。
# -----------------------------

def calculate(a, b):
    return a + b, a - b, a * b, a / b


def main():
    result = calculate(10, 3)
    print(f"calculate(10, 3) = {result}")
    
    s, diff, p, q = calculate(10, 3)
    print(f"和: {s}, 差: {diff}, 积: {p}, 商: {q}")


if __name__ == "__main__":
    main()


# ========== 详细解析 ==========
# 函数可以返回多个值，实际上返回的是元组
# 可以用元组解包接收多个返回值