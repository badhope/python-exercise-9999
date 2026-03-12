# -----------------------------
# 题目：实现简单的命令行菜单。
# 描述：支持多级菜单和用户交互。
# -----------------------------

class MenuItem:
    def __init__(self, title, action=None):
        self.title = title
        self.action = action
        self.children = []
        self.parent = None
    
    def add_child(self, item):
        item.parent = self
        self.children.append(item)
        return item

class Menu:
    def __init__(self, title="主菜单"):
        self.root = MenuItem(title)
        self.current = self.root
        self.running = True
    
    def add_item(self, title, action=None, parent=None):
        item = MenuItem(title, action)
        if parent:
            parent.add_child(item)
        else:
            self.root.add_child(item)
        return item
    
    def display(self):
        print(f"\n{'='*40}")
        print(f"  {self.current.title}")
        print(f"{'='*40}")
        
        for i, child in enumerate(self.current.children, 1):
            print(f"  {i}. {child.title}")
        
        if self.current.parent:
            print(f"  0. 返回上级")
        else:
            print(f"  0. 退出")
        print(f"{'='*40}")
    
    def process(self, choice):
        try:
            choice = int(choice)
            
            if choice == 0:
                if self.current.parent:
                    self.current = self.current.parent
                else:
                    self.running = False
                return
            
            if 1 <= choice <= len(self.current.children):
                selected = self.current.children[choice - 1]
                
                if selected.action:
                    selected.action()
                elif selected.children:
                    self.current = selected
                else:
                    print("该选项没有子菜单或操作")
            else:
                print("无效选择，请重试")
        except ValueError:
            print("请输入数字")
    
    def run(self):
        while self.running:
            self.display()
            choice = input("请选择: ")
            self.process(choice)

def main():
    menu = Menu("系统菜单")
    
    def hello():
        print("你好!")
    
    def goodbye():
        print("再见!")
        menu.running = False
    
    menu.add_item("问候", hello)
    menu.add_item("退出", goodbye)
    
    settings = menu.add_item("设置")
    menu.add_item("主题设置", lambda: print("主题设置"), settings)
    menu.add_item("语言设置", lambda: print("语言设置"), settings)
    
    menu.run()


if __name__ == "__main__":
    main()
