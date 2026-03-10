# -----------------------------
# 题目：不同路径II。
# 描述：计算有障碍物的不同路径数。
# -----------------------------

def unique_paths_with_obstacle(obstacle_grid):
    m, n = len(obstacle_grid), len(obstacle_grid[0])
    dp = [[0] * n for _ in range(m)]
    dp[0][0] = 1 if obstacle_grid[0][0] == 0 else 0
    for i in range(m):
        for j in range(n):
            if obstacle_grid[i][j] == 1:
                dp[i][j] = 0
            else:
                if i > 0:
                    dp[i][j] += dp[i-1][j]
                if j > 0:
                    dp[i][j] += dp[i][j-1]
    return dp[m-1][n-1]

def main():
    grid = [[0,0,0],[0,1,0],[0,0,0]]
    print(f"路径数: {unique_paths_with_obstacle(grid)}")


if __name__ == "__main__":
    main()
