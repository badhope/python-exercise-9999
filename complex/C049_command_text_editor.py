# -----------------------------
# 题目：命令模式实现文本编辑器操作。
# -----------------------------

class TextDocument:
    def __init__(self):
        self.content = ""
        self.cursor = 0
    
    def insert(self, text):
        self.content = self.content[:self.cursor] + text + self.content[self.cursor:]
        self.cursor += len(text)
    
    def delete(self, length):
        deleted = self.content[self.cursor:self.cursor + length]
        self.content = self.content[:self.cursor] + self.content[self.cursor + length:]
        return deleted
    
    def move_cursor(self, position):
        self.cursor = max(0, min(position, len(self.content)))
    
    def get_content(self):
        return self.content

class Command:
    def execute(self):
        pass
    
    def undo(self):
        pass
    
    def get_description(self):
        pass

class InsertCommand(Command):
    def __init__(self, document, text):
        self.document = document
        self.text = text
        self.position = document.cursor
    
    def execute(self):
        self.document.move_cursor(self.position)
        self.document.insert(self.text)
    
    def undo(self):
        self.document.move_cursor(self.position)
        self.document.delete(len(self.text))
    
    def get_description(self):
        return f"插入: {self.text}"

class DeleteCommand(Command):
    def __init__(self, document, length):
        self.document = document
        self.length = length
        self.deleted_text = ""
        self.position = document.cursor
    
    def execute(self):
        self.document.move_cursor(self.position)
        self.deleted_text = self.document.delete(self.length)
    
    def undo(self):
        self.document.move_cursor(self.position)
        self.document.insert(self.deleted_text)
    
    def get_description(self):
        return f"删除: {self.deleted_text}"

class ReplaceCommand(Command):
    def __init__(self, document, old_text, new_text):
        self.document = document
        self.old_text = old_text
        self.new_text = new_text
        self.positions = []
    
    def execute(self):
        self.positions = []
        pos = 0
        while True:
            pos = self.document.content.find(self.old_text, pos)
            if pos == -1:
                break
            self.positions.append(pos)
            pos += len(self.new_text)
        
        content = self.document.content
        self.document.content = content.replace(self.old_text, self.new_text)
    
    def undo(self):
        content = self.document.content
        self.document.content = content.replace(self.new_text, self.old_text)
    
    def get_description(self):
        return f"替换: {self.old_text} -> {self.new_text}"

class CommandHistory:
    def __init__(self, max_size=50):
        self.history = []
        self.redo_stack = []
        self.max_size = max_size
    
    def push(self, command):
        self.history.append(command)
        if len(self.history) > self.max_size:
            self.history.pop(0)
        self.redo_stack.clear()
    
    def undo(self):
        if self.history:
            command = self.history.pop()
            self.redo_stack.append(command)
            return command
        return None
    
    def redo(self):
        if self.redo_stack:
            command = self.redo_stack.pop()
            self.history.append(command)
            return command
        return None
    
    def can_undo(self):
        return len(self.history) > 0
    
    def can_redo(self):
        return len(self.redo_stack) > 0

class TextEditor:
    def __init__(self):
        self.document = TextDocument()
        self.history = CommandHistory()
    
    def insert(self, text):
        command = InsertCommand(self.document, text)
        command.execute()
        self.history.push(command)
    
    def delete(self, length):
        command = DeleteCommand(self.document, length)
        command.execute()
        self.history.push(command)
    
    def replace(self, old_text, new_text):
        command = ReplaceCommand(self.document, old_text, new_text)
        command.execute()
        self.history.push(command)
    
    def undo(self):
        command = self.history.undo()
        if command:
            command.undo()
            return True
        return False
    
    def redo(self):
        command = self.history.redo()
        if command:
            command.execute()
            return True
        return False
    
    def get_content(self):
        return self.document.get_content()

def main():
    editor = TextEditor()
    
    print("=== 编辑操作 ===")
    editor.insert("Hello")
    print(f"插入Hello: {editor.get_content()}")
    
    editor.insert(" World")
    print(f"插入 World: {editor.get_content()}")
    
    editor.document.move_cursor(5)
    editor.delete(6)
    print(f"删除 World: {editor.get_content()}")
    
    print("\n=== 撤销操作 ===")
    editor.undo()
    print(f"撤销删除: {editor.get_content()}")
    
    editor.undo()
    print(f"撤销插入: {editor.get_content()}")
    
    print("\n=== 重做操作 ===")
    editor.redo()
    print(f"重做插入: {editor.get_content()}")
    
    print("\n=== 替换操作 ===")
    editor.replace("Hello", "Hi")
    print(f"替换后: {editor.get_content()}")
    
    editor.undo()
    print(f"撤销替换: {editor.get_content()}")


if __name__ == "__main__":
    main()
