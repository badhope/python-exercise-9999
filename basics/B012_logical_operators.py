# -----------------------------
# 题目：逻辑运算符练习。
# 描述：给定 x=True, y=False, z=True，计算 x and y, x or y, not x, x and y or z 的结果。
# -----------------------------

def main():
    x = True
    y = False
    z = True
    
    print(f"x = {x}, y = {y}, z = {z}")
    print(f"x and y = {x and y}")
    print(f"x or y = {x or y}")
    print(f"not x = {not x}")
    print(f"x and y or z = {x and y or z}")


if __name__ == "__main__":
    main()


# ========== 详细解析 ==========
# and：所有值为True时返回True，否则返回False
# or：任意一个值为True时返回True，否则返回False
# not：取反操作
# 短路求值：and遇到False停止，or遇到True停止