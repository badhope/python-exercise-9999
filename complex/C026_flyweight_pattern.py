# -----------------------------
# 题目：享元模式实现字符渲染优化。
# -----------------------------

class Character:
    def __init__(self, char, font, size, color):
        self.char = char
        self.font = font
        self.size = size
        self.color = color
    
    def render(self, position):
        return f"[{position}] '{self.char}' ({self.font}, {self.size}px, {self.color})"

class CharacterFactory:
    _characters = {}
    
    @classmethod
    def get_character(cls, char, font="Arial", size=12, color="black"):
        key = (char, font, size, color)
        if key not in cls._characters:
            cls._characters[key] = Character(char, font, size, color)
        return cls._characters[key]
    
    @classmethod
    def get_pool_size(cls):
        return len(cls._characters)

class TextEditor:
    def __init__(self):
        self.characters = []
    
    def insert(self, char, font="Arial", size=12, color="black", position=None):
        character = CharacterFactory.get_character(char, font, size, color)
        pos = position if position is not None else len(self.characters)
        self.characters.append((character, pos))
    
    def render(self):
        return [char.render(pos) for char, pos in self.characters]

def main():
    editor = TextEditor()
    
    text = "Hello World! 你好世界！"
    for i, char in enumerate(text):
        font = "Arial" if i < 6 else "SimSun"
        size = 14 if i % 2 == 0 else 12
        color = "red" if i < 4 else "black"
        editor.insert(char, font, size, color, i)
    
    print("渲染结果:")
    for result in editor.render():
        print(result)
    
    print(f"\n字符池大小: {CharacterFactory.get_pool_size()}")
    print(f"总字符数: {len(editor.characters)}")


if __name__ == "__main__":
    main()
