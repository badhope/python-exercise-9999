# -----------------------------
# 题目：实现简单的访问者模式。
# -----------------------------

from typing import List, Any
from abc import ABC, abstractmethod

class Visitor(ABC):
    @abstractmethod
    def visit_element_a(self, element: 'ElementA') -> Any:
        pass
    
    @abstractmethod
    def visit_element_b(self, element: 'ElementB') -> Any:
        pass

class Element(ABC):
    @abstractmethod
    def accept(self, visitor: Visitor) -> Any:
        pass

class ElementA(Element):
    def __init__(self, name: str, value: int):
        self.name = name
        self.value = value
    
    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_element_a(self)

class ElementB(Element):
    def __init__(self, title: str, items: List[str]):
        self.title = title
        self.items = items
    
    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_element_b(self)

class ObjectStructure:
    def __init__(self):
        self._elements: List[Element] = []
    
    def add(self, element: Element):
        self._elements.append(element)
    
    def remove(self, element: Element):
        self._elements.remove(element)
    
    def accept(self, visitor: Visitor) -> List[Any]:
        return [element.accept(visitor) for element in self._elements]

class PrintVisitor(Visitor):
    def visit_element_a(self, element: ElementA) -> str:
        return f"ElementA: {element.name} = {element.value}"
    
    def visit_element_b(self, element: ElementB) -> str:
        return f"ElementB: {element.title} [{', '.join(element.items)}]"

class JsonVisitor(Visitor):
    def visit_element_a(self, element: ElementA) -> dict:
        return {
            'type': 'ElementA',
            'name': element.name,
            'value': element.value
        }
    
    def visit_element_b(self, element: ElementB) -> dict:
        return {
            'type': 'ElementB',
            'title': element.title,
            'items': element.items
        }

class CountVisitor(Visitor):
    def __init__(self):
        self.element_a_count = 0
        self.element_b_count = 0
    
    def visit_element_a(self, element: ElementA) -> None:
        self.element_a_count += 1
    
    def visit_element_b(self, element: ElementB) -> None:
        self.element_b_count += 1
    
    def get_stats(self) -> dict:
        return {
            'ElementA': self.element_a_count,
            'ElementB': self.element_b_count,
            'total': self.element_a_count + self.element_b_count
        }

class FileElement(Element):
    def __init__(self, name: str, size: int):
        self.name = name
        self.size = size
    
    def accept(self, visitor: Visitor) -> Any:
        if hasattr(visitor, 'visit_file'):
            return visitor.visit_file(self)
        return None

class DirectoryElement(Element):
    def __init__(self, name: str):
        self.name = name
        self._children: List[Element] = []
    
    def add(self, element: Element):
        self._children.append(element)
    
    def accept(self, visitor: Visitor) -> Any:
        if hasattr(visitor, 'visit_directory'):
            result = visitor.visit_directory(self)
            for child in self._children:
                child.accept(visitor)
            return result
        return None

class FileSystemVisitor(Visitor):
    def __init__(self):
        self.total_size = 0
        self.file_count = 0
        self.dir_count = 0
    
    def visit_element_a(self, element: ElementA) -> Any:
        pass
    
    def visit_element_b(self, element: ElementB) -> Any:
        pass
    
    def visit_file(self, element: FileElement):
        self.total_size += element.size
        self.file_count += 1
    
    def visit_directory(self, element: DirectoryElement):
        self.dir_count += 1
    
    def get_stats(self) -> dict:
        return {
            'total_size': self.total_size,
            'file_count': self.file_count,
            'dir_count': self.dir_count
        }

def main():
    structure = ObjectStructure()
    structure.add(ElementA("配置", 100))
    structure.add(ElementB("菜单", ["文件", "编辑", "视图"]))
    structure.add(ElementA("计数器", 42))
    structure.add(ElementB("列表", ["项目1", "项目2", "项目3"]))
    
    print("=== 打印访问者 ===")
    print_visitor = PrintVisitor()
    results = structure.accept(print_visitor)
    for result in results:
        print(f"  {result}")
    
    print("\n=== JSON访问者 ===")
    json_visitor = JsonVisitor()
    results = structure.accept(json_visitor)
    for result in results:
        print(f"  {result}")
    
    print("\n=== 计数访问者 ===")
    count_visitor = CountVisitor()
    structure.accept(count_visitor)
    print(f"统计: {count_visitor.get_stats()}")
    
    print("\n=== 文件系统示例 ===")
    root = DirectoryElement("root")
    root.add(FileElement("readme.txt", 1024))
    root.add(FileElement("config.json", 512))
    
    src = DirectoryElement("src")
    src.add(FileElement("main.py", 2048))
    src.add(FileElement("utils.py", 1024))
    root.add(src)
    
    fs_visitor = FileSystemVisitor()
    root.accept(fs_visitor)
    print(f"文件系统统计: {fs_visitor.get_stats()}")


if __name__ == "__main__":
    main()
