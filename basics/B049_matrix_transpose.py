# -----------------------------
# 题目：列表推导式练习。
# 描述：使用列表推导式实现矩阵转置。
# -----------------------------

def main():
    matrix = [[1, 2, 3], [4, 5, 6]]
    print(f"原矩阵: {matrix}")
    transposed = [[row[i] for row in matrix] for i in range(len(matrix[0]))]
    print(f"转置后: {transposed}")


if __name__ == "__main__":
    main()
