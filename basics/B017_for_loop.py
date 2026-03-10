# -----------------------------
# 题目：for循环基础。
# 描述：使用for循环输出1到10的整数，以及1到10的累加和。
# -----------------------------

def main():
    print("1到10的整数:")
    for i in range(1, 11):
        print(i, end=" ")
    print()
    
    total = 0
    for i in range(1, 11):
        total += i
    print(f"1到10的累加和: {total}")


if __name__ == "__main__":
    main()


# ========== 详细解析 ==========
# range(start, end)：生成从start到end-1的整数序列
# range(end)：默认从0开始
# range(start, end, step)：指定步长
# for循环常用于遍历序列或确定次数的循环