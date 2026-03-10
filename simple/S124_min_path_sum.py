# -----------------------------
# 题目：最小路径和。
# 描述：计算网格的最小路径和。
# -----------------------------

def min_path_sum(grid):
    m, n = len(grid), len(grid[0])
    for i in range(m):
        for j in range(n):
            if i == 0 and j == 0:
                continue
            elif i == 0:
                grid[i][j] += grid[i][j-1]
            elif j == 0:
                grid[i][j] += grid[i-1][j]
            else:
                grid[i][j] += min(grid[i-1][j], grid[i][j-1])
    return grid[m-1][n-1]

def main():
    grid = [[1,3,1],[1,5,1],[4,2,1]]
    print(f"最小路径和: {min_path_sum(grid)}")


if __name__ == "__main__":
    main()
