# -----------------------------
# 题目：字符串对齐。
# 描述：使用 ljust、rjust、center 对字符串进行对齐操作。
# -----------------------------

def main():
    s = "Python"
    print(f"原字符串: '{s}'")
    print(f"ljust(10): '{s.ljust(10)}'")
    print(f"rjust(10): '{s.rjust(10)}'")
    print(f"center(10): '{s.center(10)}'")


if __name__ == "__main__":
    main()
