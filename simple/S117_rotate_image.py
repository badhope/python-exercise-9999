# -----------------------------
# 题目：旋转图像。
# 描述：原地旋转n×n图像90度。
# -----------------------------

def rotate_image(matrix):
    n = len(matrix)
    matrix[:] = [list(row) for row in zip(*matrix[::-1])]

def main():
    matrix = [[1,2,3],[4,5,6],[7,8,9]]
    rotate_image(matrix)
    print(f"旋转后: {matrix}")


if __name__ == "__main__":
    main()
