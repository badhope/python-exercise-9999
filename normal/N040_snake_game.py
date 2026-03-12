# -----------------------------
# 题目：实现简单的贪吃蛇游戏逻辑。
# 描述：贪吃蛇游戏的核心逻辑。
# -----------------------------

import random
from collections import deque

class SnakeGame:
    def __init__(self, width=20, height=20):
        self.width = width
        self.height = height
        self.snake = deque()
        self.food = None
        self.direction = 'right'
        self.score = 0
        self.game_over = False
    
    def start(self):
        center_x = self.width // 2
        center_y = self.height // 2
        self.snake = deque([
            (center_x, center_y),
            (center_x - 1, center_y),
            (center_x - 2, center_y)
        ])
        self.direction = 'right'
        self.score = 0
        self.game_over = False
        self._spawn_food()
    
    def _spawn_food(self):
        while True:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if (x, y) not in self.snake:
                self.food = (x, y)
                break
    
    def set_direction(self, direction):
        opposite = {'up': 'down', 'down': 'up', 'left': 'right', 'right': 'left'}
        if direction in opposite and self.direction != opposite[direction]:
            self.direction = direction
    
    def move(self):
        if self.game_over:
            return False
        
        head_x, head_y = self.snake[0]
        
        if self.direction == 'up':
            new_head = (head_x, head_y - 1)
        elif self.direction == 'down':
            new_head = (head_x, head_y + 1)
        elif self.direction == 'left':
            new_head = (head_x - 1, head_y)
        else:
            new_head = (head_x + 1, head_y)
        
        if self._is_collision(new_head):
            self.game_over = True
            return False
        
        self.snake.appendleft(new_head)
        
        if new_head == self.food:
            self.score += 10
            self._spawn_food()
        else:
            self.snake.pop()
        
        return True
    
    def _is_collision(self, position):
        x, y = position
        
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True
        
        if position in list(self.snake)[:-1]:
            return True
        
        return False
    
    def get_board(self):
        board = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        
        for x, y in self.snake:
            if 0 <= x < self.width and 0 <= y < self.height:
                board[y][x] = 'S'
        
        if self.food:
            fx, fy = self.food
            board[fy][fx] = 'F'
        
        return board
    
    def display(self):
        board = self.get_board()
        print(f"\n得分: {self.score}")
        print('+' + '-' * self.width + '+')
        for row in board:
            print('|' + ''.join(row) + '|')
        print('+' + '-' * self.width + '+')
    
    def get_status(self):
        return {
            'snake': list(self.snake),
            'food': self.food,
            'direction': self.direction,
            'score': self.score,
            'game_over': self.game_over
        }

def main():
    game = SnakeGame(10, 10)
    game.start()
    
    print("贪吃蛇游戏")
    print("使用 w(上)/s(下)/a(左)/d(右) 控制")
    
    moves = ['right', 'right', 'down', 'down', 'left']
    
    for move in moves[:5]:
        game.set_direction(move)
        game.move()
    
    game.display()
    print(f"游戏状态: {'结束' if game.game_over else '进行中'}")


if __name__ == "__main__":
    main()
