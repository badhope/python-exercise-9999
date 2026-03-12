# -----------------------------
# 题目：实现享元模式高级版。
# -----------------------------

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from threading import Lock

@dataclass(frozen=True)
class FlyweightKey:
    shared_state: tuple

class Flyweight:
    def __init__(self, shared_state: tuple):
        self._shared_state = shared_state
    
    def operation(self, unique_state: Any) -> str:
        return f"共享状态: {self._shared_state}, 唯一状态: {unique_state}"
    
    @property
    def shared_state(self) -> tuple:
        return self._shared_state

class FlyweightFactory:
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._flyweights: Dict[FlyweightKey, Flyweight] = {}
        return cls._instance
    
    def get_flyweight(self, shared_state: tuple) -> Flyweight:
        key = FlyweightKey(shared_state)
        
        if key not in self._flyweights:
            self._flyweights[key] = Flyweight(shared_state)
        
        return self._flyweights[key]
    
    def get_count(self) -> int:
        return len(self._flyweights)
    
    def list_flyweights(self) -> List[tuple]:
        return [fw.shared_state for fw in self._flyweights.values()]

class Character:
    def __init__(self, char: str, font: str, size: int, color: str):
        self.char = char
        self.font = font
        self.size = size
        self.color = color
    
    def render(self, position: Tuple[int, int]) -> str:
        return f"'{self.char}' at {position} (font={self.font}, size={self.size}, color={self.color})"

class CharacterFactory:
    def __init__(self):
        self._characters: Dict[str, Character] = {}
    
    def get_character(self, char: str, font: str = "Arial", 
                      size: int = 12, color: str = "black") -> Character:
        key = f"{char}|{font}|{size}|{color}"
        
        if key not in self._characters:
            self._characters[key] = Character(char, font, size, color)
        
        return self._characters[key]
    
    def get_count(self) -> int:
        return len(self._characters)

class TextEditor:
    def __init__(self):
        self._factory = CharacterFactory()
        self._positions: List[Tuple[Character, Tuple[int, int]]] = []
    
    def insert(self, char: str, x: int, y: int, 
               font: str = "Arial", size: int = 12, color: str = "black"):
        character = self._factory.get_character(char, font, size, color)
        self._positions.append((character, (x, y)))
    
    def render(self) -> List[str]:
        return [char.render(pos) for char, pos in self._positions]
    
    def get_stats(self) -> dict:
        return {
            'total_characters': len(self._positions),
            'unique_characters': self._factory.get_count()
        }

class TreeType:
    def __init__(self, name: str, color: str, texture: str):
        self.name = name
        self.color = color
        self.texture = texture

class TreeFactory:
    def __init__(self):
        self._tree_types: Dict[str, TreeType] = {}
    
    def get_tree_type(self, name: str, color: str, texture: str) -> TreeType:
        key = f"{name}|{color}|{texture}"
        
        if key not in self._tree_types:
            self._tree_types[key] = TreeType(name, color, texture)
        
        return self._tree_types[key]
    
    def get_count(self) -> int:
        return len(self._tree_types)

@dataclass
class Tree:
    x: int
    y: int
    tree_type: TreeType
    
    def draw(self) -> str:
        return f"绘制{self.tree_type.name}树在({self.x}, {self.y}), 颜色:{self.tree_type.color}"

class Forest:
    def __init__(self):
        self._factory = TreeFactory()
        self._trees: List[Tree] = []
    
    def plant_tree(self, x: int, y: int, name: str, color: str, texture: str):
        tree_type = self._factory.get_tree_type(name, color, texture)
        self._trees.append(Tree(x, y, tree_type))
    
    def draw(self) -> List[str]:
        return [tree.draw() for tree in self._trees]
    
    def get_stats(self) -> dict:
        return {
            'total_trees': len(self._trees),
            'unique_types': self._factory.get_count()
        }

class Shape:
    def __init__(self, type_: str, color: str):
        self.type = type_
        self.color = color
    
    def draw(self, x: int, y: int, size: int) -> str:
        return f"绘制{self.color}的{self.type}在({x}, {y}), 大小:{size}"

class ShapeFactory:
    def __init__(self):
        self._shapes: Dict[str, Shape] = {}
    
    def get_shape(self, type_: str, color: str) -> Shape:
        key = f"{type_}|{color}"
        
        if key not in self._shapes:
            self._shapes[key] = Shape(type_, color)
        
        return self._shapes[key]
    
    def get_count(self) -> int:
        return len(self._shapes)

def main():
    print("=== 文本编辑器 ===")
    editor = TextEditor()
    
    editor.insert("H", 0, 0, "Arial", 12, "black")
    editor.insert("e", 1, 0, "Arial", 12, "black")
    editor.insert("l", 2, 0, "Arial", 12, "black")
    editor.insert("l", 3, 0, "Arial", 12, "black")
    editor.insert("o", 4, 0, "Arial", 12, "black")
    
    for line in editor.render():
        print(f"  {line}")
    
    print(f"统计: {editor.get_stats()}")
    
    print("\n=== 森林 ===")
    forest = Forest()
    
    forest.plant_tree(0, 0, "橡树", "绿色", "粗糙")
    forest.plant_tree(10, 5, "松树", "深绿", "光滑")
    forest.plant_tree(20, 10, "橡树", "绿色", "粗糙")
    forest.plant_tree(30, 15, "橡树", "绿色", "粗糙")
    
    for line in forest.draw():
        print(f"  {line}")
    
    print(f"统计: {forest.get_stats()}")
    
    print("\n=== Flyweight工厂 ===")
    factory = FlyweightFactory()
    
    fw1 = factory.get_flyweight(("共享数据1", "共享数据2"))
    fw2 = factory.get_flyweight(("共享数据1", "共享数据2"))
    fw3 = factory.get_flyweight(("其他数据",))
    
    print(f"fw1 is fw2: {fw1 is fw2}")
    print(f"fw1 is fw3: {fw1 is fw3}")
    print(f"享元数量: {factory.get_count()}")


if __name__ == "__main__":
    main()
