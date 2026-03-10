# -----------------------------
# 题目：类型转换练习。
# 描述：将字符串 "123" 转换为整数，浮点数 3.14 转换为整数，整数 99 转换为字符串。
# -----------------------------

def main():
    s = "123"
    f = 3.14
    n = 99

    int_from_str = int(s)
    int_from_float = int(f)
    str_from_int = str(n)

    print(f"字符串转整数: int('{s}') = {int_from_str}")
    print(f"浮点数转整数: int({f}) = {int_from_float}")
    print(f"整数转字符串: str({n}) = {str_from_int}")


if __name__ == "__main__":
    main()


# ========== 详细解析 ==========
# int()：将字符串或浮点数转换为整数（截断小数部分）
# str()：将数值转换为字符串
# float()：将字符串或整数转换为浮点数