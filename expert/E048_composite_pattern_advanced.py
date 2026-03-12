# -----------------------------
# 题目：实现组合模式高级版。
# -----------------------------

from typing import List, Optional, Any, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass

class Component(ABC):
    @abstractmethod
    def operation(self) -> str:
        pass
    
    @abstractmethod
    def add(self, component: 'Component'):
        pass
    
    @abstractmethod
    def remove(self, component: 'Component'):
        pass
    
    @abstractmethod
    def get_child(self, index: int) -> Optional['Component']:
        pass

class Leaf(Component):
    def __init__(self, name: str):
        self.name = name
    
    def operation(self) -> str:
        return self.name
    
    def add(self, component: Component):
        raise NotImplementedError("叶子节点不能添加子节点")
    
    def remove(self, component: Component):
        raise NotImplementedError("叶子节点不能移除子节点")
    
    def get_child(self, index: int) -> Optional[Component]:
        return None

class Composite(Component):
    def __init__(self, name: str):
        self.name = name
        self._children: List[Component] = []
    
    def operation(self) -> str:
        results = [child.operation() for child in self._children]
        return f"{self.name} [{', '.join(results)}]"
    
    def add(self, component: Component):
        self._children.append(component)
    
    def remove(self, component: Component):
        self._children.remove(component)
    
    def get_child(self, index: int) -> Optional[Component]:
        if 0 <= index < len(self._children):
            return self._children[index]
        return None
    
    def get_children(self) -> List[Component]:
        return self._children.copy()

class FileSystemComponent(ABC):
    @abstractmethod
    def get_size(self) -> int:
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        pass
    
    @abstractmethod
    def print_structure(self, indent: int = 0):
        pass

class File(FileSystemComponent):
    def __init__(self, name: str, size: int):
        self._name = name
        self._size = size
    
    def get_size(self) -> int:
        return self._size
    
    def get_name(self) -> str:
        return self._name
    
    def print_structure(self, indent: int = 0):
        print("  " * indent + f"- {self._name} ({self._size}KB)")

class Directory(FileSystemComponent):
    def __init__(self, name: str):
        self._name = name
        self._children: List[FileSystemComponent] = []
    
    def add(self, component: FileSystemComponent):
        self._children.append(component)
    
    def remove(self, component: FileSystemComponent):
        self._children.remove(component)
    
    def get_size(self) -> int:
        return sum(child.get_size() for child in self._children)
    
    def get_name(self) -> str:
        return self._name
    
    def print_structure(self, indent: int = 0):
        print("  " * indent + f"+ {self._name}/")
        for child in self._children:
            child.print_structure(indent + 1)

class TreeNode:
    def __init__(self, value: Any):
        self.value = value
        self._children: List['TreeNode'] = []
        self._parent: Optional['TreeNode'] = None
    
    def add_child(self, child: 'TreeNode'):
        child._parent = self
        self._children.append(child)
    
    def remove_child(self, child: 'TreeNode'):
        child._parent = None
        self._children.remove(child)
    
    def get_children(self) -> List['TreeNode']:
        return self._children.copy()
    
    def get_parent(self) -> Optional['TreeNode']:
        return self._parent
    
    def is_root(self) -> bool:
        return self._parent is None
    
    def is_leaf(self) -> bool:
        return len(self._children) == 0
    
    def get_depth(self) -> int:
        depth = 0
        current = self._parent
        while current:
            depth += 1
            current = current._parent
        return depth
    
    def traverse(self, callback: Callable):
        callback(self)
        for child in self._children:
            child.traverse(callback)

class OrganizationComponent(ABC):
    @abstractmethod
    def get_name(self) -> str:
        pass
    
    @abstractmethod
    def get_budget(self) -> float:
        pass
    
    @abstractmethod
    def get_employee_count(self) -> int:
        pass

class Employee(OrganizationComponent):
    def __init__(self, name: str, salary: float):
        self._name = name
        self._salary = salary
    
    def get_name(self) -> str:
        return self._name
    
    def get_budget(self) -> float:
        return self._salary
    
    def get_employee_count(self) -> int:
        return 1

class Department(OrganizationComponent):
    def __init__(self, name: str):
        self._name = name
        self._members: List[OrganizationComponent] = []
    
    def add(self, member: OrganizationComponent):
        self._members.append(member)
    
    def get_name(self) -> str:
        return self._name
    
    def get_budget(self) -> float:
        return sum(member.get_budget() for member in self._members)
    
    def get_employee_count(self) -> int:
        return sum(member.get_employee_count() for member in self._members)

def main():
    print("=== 文件系统 ===")
    root = Directory("root")
    src = Directory("src")
    docs = Directory("docs")
    
    src.add(File("main.py", 10))
    src.add(File("utils.py", 5))
    docs.add(File("readme.md", 3))
    root.add(src)
    root.add(docs)
    root.add(File("config.json", 1))
    
    root.print_structure()
    print(f"总大小: {root.get_size()}KB")
    
    print("\n=== 树结构 ===")
    root_node = TreeNode("根")
    child1 = TreeNode("子节点1")
    child2 = TreeNode("子节点2")
    
    root_node.add_child(child1)
    root_node.add_child(child2)
    child1.add_child(TreeNode("孙节点1"))
    
    def print_node(node):
        print("  " * node.get_depth() + f"- {node.value}")
    
    root_node.traverse(print_node)
    
    print("\n=== 组织结构 ===")
    company = Department("公司")
    tech = Department("技术部")
    sales = Department("销售部")
    
    tech.add(Employee("张三", 15000))
    tech.add(Employee("李四", 12000))
    sales.add(Employee("王五", 10000))
    
    company.add(tech)
    company.add(sales)
    
    print(f"公司预算: {company.get_budget()}")
    print(f"员工数量: {company.get_employee_count()}")


if __name__ == "__main__":
    main()
