# -----------------------------
# 题目：图书管理系统。
# 描述：实现图书管理系统，支持增删改查。
# -----------------------------

class Book:
    def __init__(self, isbn, title, author, price):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.price = price
    
    def __str__(self):
        return f"ISBN: {self.isbn}, 书名: {self.title}, 作者: {self.author}, 价格: {self.price}"

class Library:
    def __init__(self):
        self.books = {}
    
    def add_book(self, book):
        self.books[book.isbn] = book
    
    def remove_book(self, isbn):
        if isbn in self.books:
            del self.books[isbn]
            return True
        return False
    
    def find_book(self, isbn):
        return self.books.get(isbn)
    
    def list_books(self):
        return list(self.books.values())

def main():
    lib = Library()
    lib.add_book(Book("978-7-111-54742-6", "Python编程", "张三", 89.0))
    lib.add_book(Book("978-7-115-42835-1", "算法导论", "李四", 128.0))
    print("图书列表:")
    for book in lib.list_books():
        print(book)


if __name__ == "__main__":
    main()
