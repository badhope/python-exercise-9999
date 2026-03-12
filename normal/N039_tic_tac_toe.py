# -----------------------------
# 题目：实现简单的井字棋游戏。
# 描述：双人对战的井字棋游戏。
# -----------------------------

class TicTacToe:
    def __init__(self):
        self.board = [[' ' for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'
        self.winner = None
        self.game_over = False
        self.moves_count = 0
    
    def reset(self):
        self.board = [[' ' for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'
        self.winner = None
        self.game_over = False
        self.moves_count = 0
    
    def make_move(self, row, col):
        if self.game_over:
            return False, "游戏已结束"
        
        if not (0 <= row < 3 and 0 <= col < 3):
            return False, "位置无效"
        
        if self.board[row][col] != ' ':
            return False, "位置已被占用"
        
        self.board[row][col] = self.current_player
        self.moves_count += 1
        
        if self._check_winner():
            self.winner = self.current_player
            self.game_over = True
            return True, f"玩家 {self.current_player} 获胜!"
        
        if self.moves_count == 9:
            self.game_over = True
            return True, "平局!"
        
        self.current_player = 'O' if self.current_player == 'X' else 'X'
        return True, f"轮到玩家 {self.current_player}"
    
    def _check_winner(self):
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] != ' ':
                return True
            if self.board[0][i] == self.board[1][i] == self.board[2][i] != ' ':
                return True
        
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != ' ':
            return True
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != ' ':
            return True
        
        return False
    
    def display(self):
        print("\n  0 1 2")
        for i, row in enumerate(self.board):
            print(f"{i} {'|'.join(row)}")
            if i < 2:
                print("  -+-+-")
    
    def get_board(self):
        return [row[:] for row in self.board]
    
    def get_status(self):
        return {
            'board': self.get_board(),
            'current_player': self.current_player,
            'winner': self.winner,
            'game_over': self.game_over
        }
    
    def get_available_moves(self):
        moves = []
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == ' ':
                    moves.append((i, j))
        return moves

def main():
    game = TicTacToe()
    
    print("井字棋游戏")
    print("玩家 X 先手")
    
    while not game.game_over:
        game.display()
        try:
            row = int(input(f"玩家 {game.current_player} - 输入行(0-2): "))
            col = int(input(f"玩家 {game.current_player} - 输入列(0-2): "))
            success, message = game.make_move(row, col)
            print(message)
        except ValueError:
            print("请输入数字")
    
    game.display()
    if game.winner:
        print(f"玩家 {game.winner} 获胜!")
    else:
        print("平局!")


if __name__ == "__main__":
    main()
