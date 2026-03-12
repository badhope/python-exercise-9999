# -----------------------------
# 题目：简易文本编辑器。
# 描述：实现文本的统计、查找、替换功能。
# -----------------------------

class TextEditor:
    def __init__(self, text=""):
        self.text = text
    
    def word_count(self):
        return len(self.text.split())
    
    def char_count(self):
        return len(self.text)
    
    def find(self, word):
        return self.text.count(word)
    
    def replace(self, old, new):
        self.text = self.text.replace(old, new)
    
    def to_upper(self):
        return self.text.upper()
    
    def to_lower(self):
        return self.text.lower()

def main():
    editor = TextEditor("Hello World! Hello Python!")
    print(f"字数: {editor.word_count()}")
    print(f"'Hello' 出现次数: {editor.find('Hello')}")


if __name__ == "__main__":
    main()
