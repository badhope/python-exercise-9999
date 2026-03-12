# -----------------------------
# 题目：实现简单的猜词游戏。
# 描述：类似Hangman的猜词游戏。
# -----------------------------

import random

class WordGuessGame:
    def __init__(self):
        self.words = [
            'python', 'programming', 'computer', 'algorithm', 'database',
            'network', 'software', 'hardware', 'developer', 'interface',
            'variable', 'function', 'class', 'object', 'method'
        ]
        self.word = ''
        self.guessed = set()
        self.max_attempts = 6
        self.attempts = 0
        self.game_over = False
        self.won = False
    
    def start(self):
        self.word = random.choice(self.words).lower()
        self.guessed = set()
        self.attempts = 0
        self.game_over = False
        self.won = False
    
    def guess(self, letter):
        if self.game_over:
            return "游戏已结束"
        
        letter = letter.lower()
        
        if len(letter) != 1 or not letter.isalpha():
            return "请输入单个字母"
        
        if letter in self.guessed:
            return f"字母 '{letter}' 已经猜过了"
        
        self.guessed.add(letter)
        
        if letter not in self.word:
            self.attempts += 1
            if self.attempts >= self.max_attempts:
                self.game_over = True
                self.won = False
                return f"游戏结束! 答案是: {self.word}"
            return f"错误! 还剩 {self.max_attempts - self.attempts} 次机会"
        
        if self._is_won():
            self.game_over = True
            self.won = True
            return f"恭喜! 你猜对了: {self.word}"
        
        return "正确!"
    
    def _is_won(self):
        return all(c in self.guessed for c in self.word)
    
    def get_display(self):
        display = ''
        for c in self.word:
            if c in self.guessed:
                display += c + ' '
            else:
                display += '_ '
        return display.strip()
    
    def get_status(self):
        return {
            'word_display': self.get_display(),
            'guessed': sorted(self.guessed),
            'attempts_left': self.max_attempts - self.attempts,
            'game_over': self.game_over,
            'won': self.won
        }
    
    def get_hint(self):
        unguessed = [c for c in self.word if c not in self.guessed]
        if unguessed:
            return f"提示: 单词中包含字母 '{random.choice(unguessed)}'"
        return "没有更多提示"

def main():
    game = WordGuessGame()
    game.start()
    
    print("猜词游戏开始!")
    print(f"单词长度: {len(game.word)}")
    print(f"最大尝试次数: {game.max_attempts}")
    
    while not game.game_over:
        print(f"\n当前状态: {game.get_display()}")
        print(f"已猜字母: {', '.join(game.guessed) if game.guessed else '无'}")
        print(f"剩余次数: {game.max_attempts - game.attempts}")
        
        letter = input("猜一个字母: ")
        result = game.guess(letter)
        print(result)
    
    if game.won:
        print("你赢了!")
    else:
        print("你输了!")


if __name__ == "__main__":
    main()
