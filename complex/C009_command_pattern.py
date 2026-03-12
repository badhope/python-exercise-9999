# -----------------------------
# 题目：命令模式实现操作记录。
# 描述：使用命令模式实现可撤销的操作。
# -----------------------------

class Command:
    def execute(self):
        pass
    
    def undo(self):
        pass

class TextEditor:
    def __init__(self):
        self.text = ""
    
    def write(self, text):
        self.text += text
    
    def delete(self, length):
        deleted = self.text[-length:]
        self.text = self.text[:-length]
        return deleted

class WriteCommand(Command):
    def __init__(self, editor, text):
        self.editor = editor
        self.text = text
    
    def execute(self):
        self.editor.write(self.text)
    
    def undo(self):
        self.editor.delete(len(self.text))

class CommandManager:
    def __init__(self):
        self.history = []
    
    def execute(self, command):
        command.execute()
        self.history.append(command)
    
    def undo(self):
        if self.history:
            command = self.history.pop()
            command.undo()

def main():
    editor = TextEditor()
    manager = CommandManager()
    
    manager.execute(WriteCommand(editor, "Hello "))
    manager.execute(WriteCommand(editor, "World!"))
    print(f"当前文本: {editor.text}")
    
    manager.undo()
    print(f"撤销后: {editor.text}")


if __name__ == "__main__":
    main()
