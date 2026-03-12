# -----------------------------
# 题目：实现图书管理系统。
# 描述：管理图书借阅、归还、查询等功能。
# -----------------------------

from datetime import datetime, timedelta

class Book:
    def __init__(self, book_id, title, author, isbn):
        self.id = book_id
        self.title = title
        self.author = author
        self.isbn = isbn
        self.is_borrowed = False
        self.borrower = None
        self.borrow_date = None
        self.due_date = None
    
    def borrow(self, user_id, days=30):
        if self.is_borrowed:
            return False
        self.is_borrowed = True
        self.borrower = user_id
        self.borrow_date = datetime.now()
        self.due_date = datetime.now() + timedelta(days=days)
        return True
    
    def return_book(self):
        if not self.is_borrowed:
            return False
        self.is_borrowed = False
        self.borrower = None
        self.borrow_date = None
        self.due_date = None
        return True
    
    def is_overdue(self):
        if self.is_borrowed and self.due_date:
            return datetime.now() > self.due_date
        return False

class LibraryUser:
    def __init__(self, user_id, name):
        self.id = user_id
        self.name = name
        self.borrowed_books = []
        self.max_books = 5
    
    def can_borrow(self):
        return len(self.borrowed_books) < self.max_books
    
    def add_book(self, book_id):
        if self.can_borrow():
            self.borrowed_books.append(book_id)
            return True
        return False
    
    def remove_book(self, book_id):
        if book_id in self.borrowed_books:
            self.borrowed_books.remove(book_id)
            return True
        return False

class LibrarySystem:
    def __init__(self):
        self.books = {}
        self.users = {}
        self.next_book_id = 1
        self.next_user_id = 1
    
    def add_book(self, title, author, isbn):
        book = Book(self.next_book_id, title, author, isbn)
        self.books[self.next_book_id] = book
        self.next_book_id += 1
        return book.id
    
    def add_user(self, name):
        user = LibraryUser(self.next_user_id, name)
        self.users[self.next_user_id] = user
        self.next_user_id += 1
        return user.id
    
    def borrow_book(self, user_id, book_id):
        book = self.books.get(book_id)
        user = self.users.get(user_id)
        
        if not book or not user:
            return False, "图书或用户不存在"
        
        if not user.can_borrow():
            return False, "借书数量已达上限"
        
        if book.borrow(user_id):
            user.add_book(book_id)
            return True, f"借阅成功，应还日期: {book.due_date.strftime('%Y-%m-%d')}"
        
        return False, "图书已被借出"
    
    def return_book(self, user_id, book_id):
        book = self.books.get(book_id)
        user = self.users.get(user_id)
        
        if not book or not user:
            return False, "图书或用户不存在"
        
        if book.borrower != user_id:
            return False, "该图书不是此用户借阅的"
        
        book.return_book()
        user.remove_book(book_id)
        return True, "归还成功"
    
    def search_books(self, keyword):
        results = []
        keyword = keyword.lower()
        for book in self.books.values():
            if (keyword in book.title.lower() or 
                keyword in book.author.lower() or
                keyword in book.isbn):
                results.append(book)
        return results
    
    def get_overdue_books(self):
        return [book for book in self.books.values() if book.is_overdue()]
    
    def get_user_borrowed(self, user_id):
        user = self.users.get(user_id)
        if user:
            return [self.books[bid] for bid in user.borrowed_books if bid in self.books]
        return []
    
    def get_stats(self):
        total = len(self.books)
        borrowed = sum(1 for b in self.books.values() if b.is_borrowed)
        overdue = len(self.get_overdue_books())
        
        return {
            'total_books': total,
            'borrowed_books': borrowed,
            'available_books': total - borrowed,
            'overdue_books': overdue,
            'total_users': len(self.users)
        }

def main():
    library = LibrarySystem()
    
    b1 = library.add_book("Python编程", "张三", "ISBN001")
    b2 = library.add_book("数据结构", "李四", "ISBN002")
    b3 = library.add_book("算法导论", "王五", "ISBN003")
    
    u1 = library.add_user("小明")
    u2 = library.add_user("小红")
    
    library.borrow_book(u1, b1)
    library.borrow_book(u2, b2)
    
    print("图书馆统计:")
    stats = library.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n搜索'Python':")
    results = library.search_books("Python")
    for book in results:
        status = "已借出" if book.is_borrowed else "可借"
        print(f"  {book.title} - {status}")


if __name__ == "__main__":
    main()
