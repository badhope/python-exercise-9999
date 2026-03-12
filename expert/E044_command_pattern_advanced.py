# -----------------------------
# 题目：实现命令模式高级版。
# -----------------------------

from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
from datetime import datetime
import json

class Command(ABC):
    @abstractmethod
    def execute(self) -> Any:
        pass
    
    @abstractmethod
    def undo(self) -> Any:
        pass
    
    @abstractmethod
    def redo(self) -> Any:
        pass

@dataclass
class CommandResult:
    success: bool
    data: Any = None
    error: str = None

class SimpleCommand(Command):
    def __init__(self, execute_func: Callable, undo_func: Callable = None):
        self._execute_func = execute_func
        self._undo_func = undo_func
        self._last_result = None
    
    def execute(self) -> Any:
        self._last_result = self._execute_func()
        return self._last_result
    
    def undo(self) -> Any:
        if self._undo_func:
            return self._undo_func(self._last_result)
        return None
    
    def redo(self) -> Any:
        return self.execute()

class MacroCommand(Command):
    def __init__(self, name: str = ""):
        self.name = name
        self._commands: List[Command] = []
        self._executed: List[Command] = []
    
    def add(self, command: Command):
        self._commands.append(command)
    
    def execute(self) -> List[Any]:
        results = []
        for command in self._commands:
            result = command.execute()
            results.append(result)
            self._executed.append(command)
        return results
    
    def undo(self) -> List[Any]:
        results = []
        for command in reversed(self._executed):
            result = command.undo()
            results.append(result)
        self._executed.clear()
        return results
    
    def redo(self) -> List[Any]:
        return self.execute()

class CommandHistory:
    def __init__(self, max_size: int = 100):
        self._history: List[Command] = []
        self._max_size = max_size
        self._current_index = -1
    
    def push(self, command: Command):
        if self._current_index < len(self._history) - 1:
            self._history = self._history[:self._current_index + 1]
        
        self._history.append(command)
        
        if len(self._history) > self._max_size:
            self._history.pop(0)
        else:
            self._current_index += 1
    
    def undo(self) -> Optional[Command]:
        if self._current_index >= 0:
            command = self._history[self._current_index]
            self._current_index -= 1
            return command
        return None
    
    def redo(self) -> Optional[Command]:
        if self._current_index < len(self._history) - 1:
            self._current_index += 1
            return self._history[self._current_index]
        return None
    
    def can_undo(self) -> bool:
        return self._current_index >= 0
    
    def can_redo(self) -> bool:
        return self._current_index < len(self._history) - 1

class CommandInvoker:
    def __init__(self):
        self._history = CommandHistory()
    
    def execute(self, command: Command) -> Any:
        result = command.execute()
        self._history.push(command)
        return result
    
    def undo(self) -> Any:
        command = self._history.undo()
        if command:
            return command.undo()
        return None
    
    def redo(self) -> Any:
        command = self._history.redo()
        if command:
            return command.redo()
        return None
    
    def can_undo(self) -> bool:
        return self._history.can_undo()
    
    def can_redo(self) -> bool:
        return self._history.can_redo()

class TextEditor:
    def __init__(self):
        self._content = ""
        self._invoker = CommandInvoker()
    
    def insert(self, position: int, text: str):
        old_content = self._content
        
        def execute():
            self._content = self._content[:position] + text + self._content[position:]
            return self._content
        
        def undo(result):
            self._content = old_content
            return self._content
        
        command = SimpleCommand(execute, undo)
        return self._invoker.execute(command)
    
    def delete(self, position: int, length: int):
        old_content = self._content
        deleted = self._content[position:position + length]
        
        def execute():
            self._content = self._content[:position] + self._content[position + length:]
            return self._content
        
        def undo(result):
            self._content = old_content
            return self._content
        
        command = SimpleCommand(execute, undo)
        return self._invoker.execute(command)
    
    def undo(self):
        return self._invoker.undo()
    
    def redo(self):
        return self._invoker.redo()
    
    def get_content(self) -> str:
        return self._content

class CommandQueue:
    def __init__(self):
        self._queue: List[Command] = []
    
    def enqueue(self, command: Command):
        self._queue.append(command)
    
    def execute_all(self) -> List[Any]:
        results = []
        while self._queue:
            command = self._queue.pop(0)
            results.append(command.execute())
        return results

def main():
    print("=== 文本编辑器 ===")
    editor = TextEditor()
    
    print(f"初始内容: '{editor.get_content()}'")
    
    editor.insert(0, "Hello")
    print(f"插入Hello: '{editor.get_content()}'")
    
    editor.insert(5, " World")
    print(f"插入 World: '{editor.get_content()}'")
    
    editor.undo()
    print(f"撤销: '{editor.get_content()}'")
    
    editor.redo()
    print(f"重做: '{editor.get_content()}'")
    
    print("\n=== 宏命令 ===")
    macro = MacroCommand("批量操作")
    
    values = []
    
    macro.add(SimpleCommand(lambda: values.append(1) or values.copy()))
    macro.add(SimpleCommand(lambda: values.append(2) or values.copy()))
    macro.add(SimpleCommand(lambda: values.append(3) or values.copy()))
    
    print(f"执行宏命令: {macro.execute()}")
    
    print("\n=== 命令队列 ===")
    queue = CommandQueue()
    
    results = []
    queue.enqueue(SimpleCommand(lambda: results.append("A") or results.copy()))
    queue.enqueue(SimpleCommand(lambda: results.append("B") or results.copy()))
    queue.enqueue(SimpleCommand(lambda: results.append("C") or results.copy()))
    
    print(f"执行队列: {queue.execute_all()}")


if ___name__ == "__main__":
    main()
