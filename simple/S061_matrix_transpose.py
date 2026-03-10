# -----------------------------
# 题目：矩阵转置。
# 描述：实现矩阵转置。
# -----------------------------

def matrix_transpose(matrix):
    return [[matrix[i][j] for i in range(len(matrix))] for j in range(len(matrix[0]))]

def main():
    matrix = [[1, 2, 3], [4, 5, 6]]
    print(f"转置后: {matrix_transpose(matrix)}")


if __name__ == "__main__":
    main()
