# -----------------------------
# 题目：单词搜索。
# 描述：在二维网格中搜索单词。
# -----------------------------

def exist(board, word):
    def dfs(i, j, pos):
        if pos == len(word):
            return True
        if i < 0 or i >= len(board) or j < 0 or j >= len(board[0]) or board[i][j] != word[pos]:
            return False
        temp = board[i][j]
        board[i][j] = '#'
        found = dfs(i+1, j, pos+1) or dfs(i-1, j, pos+1) or dfs(i, j+1, pos+1) or dfs(i, j-1, pos+1)
        board[i][j] = temp
        return found
    for i in range(len(board)):
        for j in range(len(board[0])):
            if dfs(i, j, 0):
                return True
    return False

def main():
    board = [["A","B"],["C","D"]]
    print(f"存在: {exist(board, 'ABCD')}")


if __name__ == "__main__":
    main()
