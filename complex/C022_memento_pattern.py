# -----------------------------
# 题目：备忘录模式实现文本编辑器撤销功能。
# -----------------------------

class Memento:
    def __init__(self, state):
        self._state = state
    
    def get_state(self):
        return self._state

class TextEditor:
    def __init__(self):
        self._content = ""
    
    def write(self, text):
        self._content += text
    
    def delete(self, n):
        self._content = self._content[:-n] if n <= len(self._content) else ""
    
    def get_content(self):
        return self._content
    
    def save(self):
        return Memento(self._content)
    
    def restore(self, memento):
        self._content = memento.get_state()

class History:
    def __init__(self, max_size=10):
        self._history = []
        self._max_size = max_size
    
    def push(self, memento):
        if len(self._history) >= self._max_size:
            self._history.pop(0)
        self._history.append(memento)
    
    def pop(self):
        if self._history:
            return self._history.pop()
        return None
    
    def can_undo(self):
        return len(self._history) > 0

class EditorController:
    def __init__(self):
        self.editor = TextEditor()
        self.history = History()
    
    def write(self, text):
        self.history.push(self.editor.save())
        self.editor.write(text)
    
    def delete(self, n=1):
        if n > 0:
            self.history.push(self.editor.save())
            self.editor.delete(n)
    
    def undo(self):
        memento = self.history.pop()
        if memento:
            self.editor.restore(memento)
            return True
        return False
    
    def get_content(self):
        return self.editor.get_content()

def main():
    controller = EditorController()
    
    controller.write("Hello")
    print(f"写入后: {controller.get_content()}")
    
    controller.write(" World")
    print(f"继续写入: {controller.get_content()}")
    
    controller.delete(6)
    print(f"删除后: {controller.get_content()}")
    
    controller.undo()
    print(f"撤销删除: {controller.get_content()}")
    
    controller.undo()
    print(f"撤销写入: {controller.get_content()}")


if __name__ == "__main__":
    main()
