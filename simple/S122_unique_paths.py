# -----------------------------
# 题目：不同路径。
# 描述：计算从左上角到右下角的不同路径数。
# -----------------------------

def unique_paths(m, n):
    dp = [[1] * n for _ in range(m)]
    for i in range(1, m):
        for j in range(1, n):
            dp[i][j] = dp[i-1][j] + dp[i][j-1]
    return dp[m-1][n-1]

def main():
    print(f"3x7网格路径数: {unique_paths(3, 7)}")


if __name__ == "__main__":
    main()
