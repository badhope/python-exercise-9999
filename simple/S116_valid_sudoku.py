# -----------------------------
# 题目：有效的数独。
# 描述：判断数独是否有效。
# -----------------------------

def is_valid_sudoku(board):
    rows = [set() for _ in range(9)]
    cols = [set() for _ in range(9)]
    boxes = [set() for _ in range(9)]
    for i in range(9):
        for j in range(9):
            num = board[i][j]
            if num == '.':
                continue
            if num in rows[i] or num in cols[j] or num in boxes[(i//3)*3 + j//3]:
                return False
            rows[i].add(num)
            cols[j].add(num)
            boxes[(i//3)*3 + j//3].add(num)
    return True

def main():
    board = [
        ["5","3",".",".","7",".",".",".","."],
        ["6",".",".","1","9","5",".",".","."],
        [".","9","8",".",".",".",".","6","."],
        ["8",".",".",".","6",".",".",".","3"],
        ["4",".",".","8",".","3",".",".","1"],
        ["7",".",".",".","2",".",".",".","6"],
        [".","6",".",".",".",".","2","8","."],
        [".",".",".","4","1","9",".",".","5"],
        [".",".",".",".","8",".",".","7","9"]
    ]
    print(f"有效: {is_valid_sudoku(board)}")


if __name__ == "__main__":
    main()
