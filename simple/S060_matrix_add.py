# -----------------------------
# 题目：矩阵加法。
# 描述：实现两个矩阵的加法。
# -----------------------------

def matrix_add(A, B):
    return [[A[i][j] + B[i][j] for j in range(len(A[0]))] for i in range(len(A))]

def main():
    A = [[1, 2], [3, 4]]
    B = [[5, 6], [7, 8]]
    print(f"矩阵加法: {matrix_add(A, B)}")


if __name__ == "__main__":
    main()
