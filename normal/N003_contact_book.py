# -----------------------------
# 题目：通讯录管理。
# 描述：实现通讯录的增删改查功能。
# -----------------------------

class ContactBook:
    def __init__(self):
        self.contacts = {}
    
    def add(self, name, phone):
        self.contacts[name] = phone
    
    def delete(self, name):
        if name in self.contacts:
            del self.contacts[name]
            return True
        return False
    
    def update(self, name, phone):
        if name in self.contacts:
            self.contacts[name] = phone
            return True
        return False
    
    def search(self, name):
        return self.contacts.get(name)
    
    def list_all(self):
        return self.contacts.copy()

def main():
    book = ContactBook()
    book.add("张三", "13800138000")
    book.add("李四", "13900139000")
    print(f"张三的电话: {book.search('张三')}")


if __name__ == "__main__":
    main()
