# -----------------------------
# 题目：二维列表操作。
# 描述：创建和操作二维列表（矩阵）。
# -----------------------------

def main():
    matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    print(f"二维列表: {matrix}")
    print(f"第2行: {matrix[1]}")
    print(f"第2行第3列: {matrix[1][2]}")
    
    for row in matrix:
        print(row)


if __name__ == "__main__":
    main()
