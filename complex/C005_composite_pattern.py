# -----------------------------
# 题目：组合模式实现文件系统。
# 描述：使用组合模式实现文件和目录的统一处理。
# -----------------------------

class FileSystemComponent:
    def display(self, indent=0):
        pass

class File(FileSystemComponent):
    def __init__(self, name):
        self.name = name
    
    def display(self, indent=0):
        print("  " * indent + f"📄 {self.name}")

class Directory(FileSystemComponent):
    def __init__(self, name):
        self.name = name
        self.children = []
    
    def add(self, component):
        self.children.append(component)
    
    def remove(self, component):
        self.children.remove(component)
    
    def display(self, indent=0):
        print("  " * indent + f"📁 {self.name}/")
        for child in self.children:
            child.display(indent + 1)

def main():
    root = Directory("root")
    root.add(File("readme.txt"))
    
    docs = Directory("docs")
    docs.add(File("guide.pdf"))
    docs.add(File("manual.doc"))
    root.add(docs)
    
    src = Directory("src")
    src.add(File("main.py"))
    src.add(File("utils.py"))
    root.add(src)
    
    root.display()


if __name__ == "__main__":
    main()
