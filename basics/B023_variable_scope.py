# -----------------------------
# 题目：变量作用域（局部变量、全局变量）。
# 描述：演示全局变量和局部变量的使用，以及如何使用 global 关键字在函数内修改全局变量。
# -----------------------------

global_var = 10


def modify_global():
    global global_var
    global_var = 20
    print(f"函数内修改全局变量: global_var = {global_var}")


def use_local():
    local_var = 5
    print(f"局部变量: local_var = {local_var}")


def main():
    print(f"全局变量初始值: global_var = {global_var}")
    modify_global()
    print(f"函数调用后全局变量: global_var = {global_var}")


if __name__ == "__main__":
    main()


# ========== 详细解析 ==========
# 全局变量：在函数外定义的变量，整个文件可见
# 局部变量：在函数内定义的变量，仅在函数内可见
# global：在函数内声明使用全局变量