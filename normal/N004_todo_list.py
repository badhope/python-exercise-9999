# -----------------------------
# 题目：待办事项列表。
# 描述：实现待办事项的管理功能。
# -----------------------------

class TodoList:
    def __init__(self):
        self.todos = []
    
    def add(self, task):
        self.todos.append({"task": task, "done": False})
    
    def complete(self, index):
        if 0 <= index < len(self.todos):
            self.todos[index]["done"] = True
    
    def remove(self, index):
        if 0 <= index < len(self.todos):
            self.todos.pop(index)
    
    def list_all(self):
        return self.todos
    
    def list_pending(self):
        return [t for t in self.todos if not t["done"]]

def main():
    todo = TodoList()
    todo.add("学习Python")
    todo.add("写代码")
    todo.complete(0)
    print("待办事项:")
    for i, t in enumerate(todo.list_all()):
        status = "✓" if t["done"] else "○"
        print(f"  {status} {t['task']}")


if __name__ == "__main__":
    main()
