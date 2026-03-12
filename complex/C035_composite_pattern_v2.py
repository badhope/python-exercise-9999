# -----------------------------
# 题目：组合模式实现文件系统。
# -----------------------------

class FileSystemComponent:
    def get_name(self):
        pass
    
    def get_size(self):
        pass
    
    def display(self, indent=0):
        pass

class File(FileSystemComponent):
    def __init__(self, name, size):
        self.name = name
        self.size = size
    
    def get_name(self):
        return self.name
    
    def get_size(self):
        return self.size
    
    def display(self, indent=0):
        print("  " * indent + f"📄 {self.name} ({self.size}KB)")

class Directory(FileSystemComponent):
    def __init__(self, name):
        self.name = name
        self.children = []
    
    def add(self, component):
        self.children.append(component)
    
    def remove(self, component):
        if component in self.children:
            self.children.remove(component)
    
    def get_name(self):
        return self.name
    
    def get_size(self):
        return sum(child.get_size() for child in self.children)
    
    def display(self, indent=0):
        print("  " * indent + f"📁 {self.name}/")
        for child in self.children:
            child.display(indent + 1)
    
    def find(self, name):
        if self.name == name:
            return self
        for child in self.children:
            if hasattr(child, 'find'):
                result = child.find(name)
                if result:
                    return result
            elif child.get_name() == name:
                return child
        return None

class FileSystem:
    def __init__(self):
        self.root = Directory("root")
    
    def create_path(self, path):
        parts = path.strip('/').split('/')
        current = self.root
        
        for part in parts[:-1]:
            found = None
            for child in current.children:
                if isinstance(child, Directory) and child.get_name() == part:
                    found = child
                    break
            
            if found:
                current = found
            else:
                new_dir = Directory(part)
                current.add(new_dir)
                current = new_dir
        
        return current
    
    def add_file(self, path, name, size):
        directory = self.create_path(path)
        directory.add(File(name, size))
    
    def add_directory(self, path, name):
        directory = self.create_path(path)
        directory.add(Directory(name))
    
    def display(self):
        self.root.display()
    
    def get_total_size(self):
        return self.root.get_size()

def main():
    fs = FileSystem()
    
    fs.add_file("/documents", "report.pdf", 1024)
    fs.add_file("/documents", "notes.txt", 50)
    fs.add_file("/documents/work", "project.doc", 2048)
    fs.add_file("/documents/work", "data.xlsx", 512)
    fs.add_file("/pictures", "photo1.jpg", 3072)
    fs.add_file("/pictures", "photo2.jpg", 2560)
    fs.add_file("/pictures/vacation", "beach.png", 4096)
    fs.add_file("/code", "main.py", 25)
    fs.add_file("/code", "utils.py", 15)
    fs.add_file("/code/tests", "test_main.py", 10)
    
    print("=== 文件系统结构 ===")
    fs.display()
    
    print(f"\n总大小: {fs.get_total_size()}KB")
    
    print("\n=== 搜索文件 ===")
    found = fs.root.find("project.doc")
    if found:
        print(f"找到文件: {found.get_name()}, 大小: {found.get_size()}KB")


if __name__ == "__main__":
    main()
