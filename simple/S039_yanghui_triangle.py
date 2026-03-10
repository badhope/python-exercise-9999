# -----------------------------
# 题目：杨辉三角。
# 描述：生成杨辉三角的前n行。
# -----------------------------

def yanghui_triangle(n):
    result = []
    for i in range(n):
        row = [1] * (i + 1)
        for j in range(1, i):
            row[j] = result[i-1][j-1] + result[i-1][j]
        result.append(row)
    return result

def main():
    for row in yanghui_triangle(5):
        print(row)


if __name__ == "__main__":
    main()
