# -----------------------------
# 题目：函数定义和调用。
# 描述：定义函数 greet(name)，返回 "Hello, {name}!"，调用并打印结果。
# -----------------------------

def greet(name):
    return f"Hello, {name}!"


def main():
    result = greet("Alice")
    print(result)


if __name__ == "__main__":
    main()


# ========== 详细解析 ==========
# def：定义函数的关键字
# 参数：在函数定义时声明的变量
# return：返回函数执行结果，如果没有return则返回None