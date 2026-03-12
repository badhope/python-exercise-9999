# -----------------------------
# 题目：迭代器模式实现自定义集合遍历。
# -----------------------------

class Iterator:
    def has_next(self):
        pass
    
    def next(self):
        pass

class Iterable:
    def get_iterator(self):
        pass

class Book:
    def __init__(self, title, author):
        self.title = title
        self.author = author
    
    def __str__(self):
        return f"《{self.title}》 - {self.author}"

class BookshelfIterator(Iterator):
    def __init__(self, books):
        self.books = books
        self.index = 0
    
    def has_next(self):
        return self.index < len(self.books)
    
    def next(self):
        if self.has_next():
            book = self.books[self.index]
            self.index += 1
            return book
        return None

class ReverseIterator(Iterator):
    def __init__(self, books):
        self.books = books
        self.index = len(books) - 1
    
    def has_next(self):
        return self.index >= 0
    
    def next(self):
        if self.has_next():
            book = self.books[self.index]
            self.index -= 1
            return book
        return None

class AuthorFilterIterator(Iterator):
    def __init__(self, books, author):
        self.filtered = [b for b in books if b.author == author]
        self.index = 0
    
    def has_next(self):
        return self.index < len(self.filtered)
    
    def next(self):
        if self.has_next():
            book = self.filtered[self.index]
            self.index += 1
            return book
        return None

class Bookshelf(Iterable):
    def __init__(self):
        self.books = []
    
    def add_book(self, book):
        self.books.append(book)
    
    def get_iterator(self):
        return BookshelfIterator(self.books)
    
    def get_reverse_iterator(self):
        return ReverseIterator(self.books)
    
    def get_author_iterator(self, author):
        return AuthorFilterIterator(self.books, author)

class TreeNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

class InOrderIterator(Iterator):
    def __init__(self, root):
        self.stack = []
        self._push_left(root)
    
    def _push_left(self, node):
        while node:
            self.stack.append(node)
            node = node.left
    
    def has_next(self):
        return len(self.stack) > 0
    
    def next(self):
        if not self.has_next():
            return None
        node = self.stack.pop()
        self._push_left(node.right)
        return node.value

def main():
    print("=== 书架遍历 ===")
    shelf = Bookshelf()
    shelf.add_book(Book("Python编程", "作者A"))
    shelf.add_book(Book("数据结构", "作者B"))
    shelf.add_book(Book("算法导论", "作者A"))
    shelf.add_book(Book("设计模式", "作者C"))
    
    print("正序遍历:")
    iterator = shelf.get_iterator()
    while iterator.has_next():
        print(f"  {iterator.next()}")
    
    print("\n逆序遍历:")
    reverse = shelf.get_reverse_iterator()
    while reverse.has_next():
        print(f"  {reverse.next()}")
    
    print("\n按作者筛选:")
    author_iter = shelf.get_author_iterator("作者A")
    while author_iter.has_next():
        print(f"  {author_iter.next()}")
    
    print("\n=== 二叉树中序遍历 ===")
    root = TreeNode(4)
    root.left = TreeNode(2)
    root.right = TreeNode(6)
    root.left.left = TreeNode(1)
    root.left.right = TreeNode(3)
    root.right.left = TreeNode(5)
    root.right.right = TreeNode(7)
    
    tree_iter = InOrderIterator(root)
    result = []
    while tree_iter.has_next():
        result.append(tree_iter.next())
    print(f"中序遍历结果: {result}")


if __name__ == "__main__":
    main()
