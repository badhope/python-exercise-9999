# -----------------------------
# 题目：原型模式实现对象克隆。
# 描述：使用原型模式实现对象的深拷贝和浅拷贝。
# -----------------------------

import copy

class Prototype:
    def clone(self):
        return copy.deepcopy(self)

class Document(Prototype):
    def __init__(self, title, content):
        self.title = title
        self.content = content
        self.metadata = {}
    
    def __str__(self):
        return f"Document(title={self.title}, content={self.content[:20]}..., metadata={self.metadata})"

def main():
    original = Document("报告", "这是一份重要报告的内容...")
    original.metadata["author"] = "张三"
    original.metadata["date"] = "2024-01-15"
    
    cloned = original.clone()
    cloned.title = "报告副本"
    cloned.metadata["author"] = "李四"
    
    print(f"原始: {original}")
    print(f"克隆: {cloned}")


if __name__ == "__main__":
    main()
