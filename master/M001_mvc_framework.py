# -----------------------------
# 题目：实现简单的MVC框架。
# 描述：实现模型-视图-控制器架构。
# -----------------------------

class Model:
    def __init__(self):
        self.data = []
        self.observers = []
    
    def add_observer(self, observer):
        self.observers.append(observer)
    
    def notify(self):
        for observer in self.observers:
            observer.update(self)
    
    def add_item(self, item):
        self.data.append(item)
        self.notify()
    
    def remove_item(self, index):
        if 0 <= index < len(self.data):
            self.data.pop(index)
            self.notify()

class View:
    def __init__(self, controller):
        self.controller = controller
    
    def update(self, model):
        print(f"数据更新: {model.data}")
    
    def display(self, model):
        print(f"当前数据: {model.data}")
    
    def get_input(self):
        return input("输入操作 (add/remove/quit): ")

class Controller:
    def __init__(self):
        self.model = Model()
        self.view = View(self)
        self.model.add_observer(self.view)
    
    def run(self):
        while True:
            self.view.display(self.model)
            action = self.view.get_input()
            if action == 'quit':
                break
            elif action == 'add':
                item = input("输入项目: ")
                self.model.add_item(item)
            elif action == 'remove':
                index = int(input("输入索引: "))
                self.model.remove_item(index)

def main():
    controller = Controller()
    print("MVC演示 (输入 add/remove/quit)")


if __name__ == "__main__":
    main()
