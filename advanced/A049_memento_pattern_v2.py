# -----------------------------
# 题目：实现简单的备忘录模式。
# -----------------------------

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import copy

@dataclass
class Memento:
    state: Dict[str, Any]
    timestamp: datetime
    description: str = ""

class Originator:
    def __init__(self):
        self._state: Dict[str, Any] = {}
    
    def set_state(self, key: str, value: Any):
        self._state[key] = value
    
    def get_state(self, key: str) -> Any:
        return self._state.get(key)
    
    def get_all_state(self) -> Dict[str, Any]:
        return self._state.copy()
    
    def save_to_memento(self, description: str = "") -> Memento:
        return Memento(
            state=copy.deepcopy(self._state),
            timestamp=datetime.now(),
            description=description
        )
    
    def restore_from_memento(self, memento: Memento):
        self._state = copy.deepcopy(memento.state)

class Caretaker:
    def __init__(self, max_history: int = 10):
        self._history: List[Memento] = []
        self._max_history = max_history
        self._current_index: int = -1
    
    def save(self, memento: Memento):
        if self._current_index < len(self._history) - 1:
            self._history = self._history[:self._current_index + 1]
        
        self._history.append(memento)
        
        if len(self._history) > self._max_history:
            self._history.pop(0)
        else:
            self._current_index += 1
    
    def undo(self) -> Optional[Memento]:
        if self._current_index > 0:
            self._current_index -= 1
            return self._history[self._current_index]
        return None
    
    def redo(self) -> Optional[Memento]:
        if self._current_index < len(self._history) - 1:
            self._current_index += 1
            return self._history[self._current_index]
        return None
    
    def get_current(self) -> Optional[Memento]:
        if 0 <= self._current_index < len(self._history):
            return self._history[self._current_index]
        return None
    
    def get_history(self) -> List[Dict]:
        return [
            {
                'index': i,
                'timestamp': m.timestamp.strftime('%H:%M:%S'),
                'description': m.description,
                'current': i == self._current_index
            }
            for i, m in enumerate(self._history)
        ]

class TextEditor:
    def __init__(self):
        self.originator = Originator()
        self.caretaker = Caretaker(max_history=20)
    
    def write(self, text: str):
        current = self.originator.get_state('content') or ''
        self.originator.set_state('content', current + text)
    
    def delete(self, count: int):
        current = self.originator.get_state('content') or ''
        self.originator.set_state('content', current[:-count] if count <= len(current) else '')
    
    def get_content(self) -> str:
        return self.originator.get_state('content') or ''
    
    def save(self, description: str = ""):
        memento = self.originator.save_to_memento(description)
        self.caretaker.save(memento)
    
    def undo(self) -> bool:
        memento = self.caretaker.undo()
        if memento:
            self.originator.restore_from_memento(memento)
            return True
        return False
    
    def redo(self) -> bool:
        memento = self.caretaker.redo()
        if memento:
            self.originator.restore_from_memento(memento)
            return True
        return False
    
    def show_history(self):
        print("历史记录:")
        for item in self.caretaker.get_history():
            marker = " <- 当前" if item['current'] else ""
            print(f"  [{item['index']}] {item['timestamp']} - {item['description']}{marker}")

class GameState:
    def __init__(self):
        self.originator = Originator()
        self.caretaker = Caretaker(max_history=5)
    
    def set_player(self, name: str, level: int, health: int, position: tuple):
        self.originator.set_state('player_name', name)
        self.originator.set_state('level', level)
        self.originator.set_state('health', health)
        self.originator.set_state('position', position)
    
    def save_checkpoint(self, checkpoint_name: str):
        memento = self.originator.save_to_memento(checkpoint_name)
        self.caretaker.save(memento)
    
    def load_checkpoint(self) -> bool:
        memento = self.caretaker.get_current()
        if memento:
            self.originator.restore_from_memento(memento)
            return True
        return False
    
    def get_state(self) -> Dict:
        return self.originator.get_all_state()

def main():
    print("=== 文本编辑器 ===")
    editor = TextEditor()
    
    editor.write("Hello")
    editor.save("写入Hello")
    
    editor.write(" World")
    editor.save("写入 World")
    
    editor.write("!")
    editor.save("写入!")
    
    print(f"当前内容: {editor.get_content()}")
    
    print("\n撤销:")
    editor.undo()
    print(f"内容: {editor.get_content()}")
    
    print("\n再次撤销:")
    editor.undo()
    print(f"内容: {editor.get_content()}")
    
    print("\n重做:")
    editor.redo()
    print(f"内容: {editor.get_content()}")
    
    editor.show_history()
    
    print("\n=== 游戏状态 ===")
    game = GameState()
    
    game.set_player("勇者", 1, 100, (0, 0))
    game.save_checkpoint("初始位置")
    
    game.set_player("勇者", 2, 85, (10, 5))
    game.save_checkpoint("村庄入口")
    
    game.set_player("勇者", 3, 60, (25, 15))
    game.save_checkpoint("Boss战前")
    
    print(f"当前状态: {game.get_state()}")


if __name__ == "__main__":
    main()
