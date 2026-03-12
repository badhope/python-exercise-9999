# -----------------------------
# 题目：实现简单的数字拼图游戏。
# 描述：滑动数字拼图游戏。
# -----------------------------

import random

class SlidingPuzzle:
    def __init__(self, size=3):
        self.size = size
        self.board = []
        self.empty_pos = (size - 1, size - 1)
        self.moves = 0
    
    def start(self):
        numbers = list(range(1, self.size * self.size)) + [0]
        self.board = []
        for i in range(self.size):
            self.board.append(numbers[i * self.size:(i + 1) * self.size])
        self.empty_pos = (self.size - 1, self.size - 1)
        self.moves = 0
        self._shuffle()
    
    def _shuffle(self):
        for _ in range(100):
            moves = self._get_valid_moves()
            if moves:
                move = random.choice(moves)
                self._move(move)
        self.moves = 0
    
    def _get_valid_moves(self):
        moves = []
        row, col = self.empty_pos
        
        if row > 0:
            moves.append('down')
        if row < self.size - 1:
            moves.append('up')
        if col > 0:
            moves.append('right')
        if col < self.size - 1:
            moves.append('left')
        
        return moves
    
    def move(self, direction):
        if direction in self._get_valid_moves():
            self._move(direction)
            return True
        return False
    
    def _move(self, direction):
        row, col = self.empty_pos
        
        if direction == 'up':
            new_row, new_col = row + 1, col
        elif direction == 'down':
            new_row, new_col = row - 1, col
        elif direction == 'left':
            new_row, new_col = row, col + 1
        elif direction == 'right':
            new_row, new_col = row, col - 1
        else:
            return
        
        self.board[row][col] = self.board[new_row][new_col]
        self.board[new_row][new_col] = 0
        self.empty_pos = (new_row, new_col)
        self.moves += 1
    
    def is_solved(self):
        expected = 1
        for i in range(self.size):
            for j in range(self.size):
                if i == self.size - 1 and j == self.size - 1:
                    if self.board[i][j] != 0:
                        return False
                else:
                    if self.board[i][j] != expected:
                        return False
                    expected += 1
        return True
    
    def display(self):
        print(f"\n移动次数: {self.moves}")
        for row in self.board:
            print(' '.join(f'{num:2d}' if num != 0 else '  ' for num in row))
    
    def get_board(self):
        return [row[:] for row in self.board]
    
    def get_moves(self):
        return self.moves

def main():
    game = SlidingPuzzle(3)
    game.start()
    
    print("数字拼图游戏")
    print("使用 w(上)/s(下)/a(左)/d(右) 移动")
    
    while not game.is_solved():
        game.display()
        move = input("移动: ").lower()
        
        direction_map = {'w': 'up', 's': 'down', 'a': 'left', 'd': 'right'}
        if move in direction_map:
            if not game.move(direction_map[move]):
                print("无效移动")
        else:
            print("使用 w/s/a/d 控制")
    
    game.display()
    print(f"恭喜完成! 总共移动 {game.moves} 次")


if __name__ == "__main__":
    main()
