# -----------------------------
# 题目：实现简单的书签管理器。
# 描述：管理浏览器书签，支持分类和搜索。
# -----------------------------

from datetime import datetime
import re

class Bookmark:
    def __init__(self, bookmark_id, url, title, category="默认", description=""):
        self.id = bookmark_id
        self.url = url
        self.title = title
        self.category = category
        self.description = description
        self.created_at = datetime.now()
        self.visit_count = 0
    
    def visit(self):
        self.visit_count += 1
    
    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'category': self.category,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'visit_count': self.visit_count
        }

class BookmarkManager:
    def __init__(self):
        self.bookmarks = {}
        self.categories = set(["默认"])
        self.next_id = 1
    
    def add(self, url, title, category="默认", description=""):
        if not self._validate_url(url):
            return None
        
        bookmark = Bookmark(self.next_id, url, title, category, description)
        self.bookmarks[self.next_id] = bookmark
        self.categories.add(category)
        self.next_id += 1
        return bookmark.id
    
    def _validate_url(self, url):
        pattern = re.compile(
            r'^https?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return bool(pattern.match(url))
    
    def get(self, bookmark_id):
        return self.bookmarks.get(bookmark_id)
    
    def delete(self, bookmark_id):
        if bookmark_id in self.bookmarks:
            del self.bookmarks[bookmark_id]
            return True
        return False
    
    def update(self, bookmark_id, **kwargs):
        bookmark = self.bookmarks.get(bookmark_id)
        if bookmark:
            for key, value in kwargs.items():
                if hasattr(bookmark, key):
                    setattr(bookmark, key, value)
                    if key == 'category':
                        self.categories.add(value)
            return True
        return False
    
    def search(self, keyword):
        results = []
        keyword = keyword.lower()
        for bookmark in self.bookmarks.values():
            if (keyword in bookmark.title.lower() or 
                keyword in bookmark.url.lower() or
                keyword in bookmark.description.lower()):
                results.append(bookmark)
        return results
    
    def get_by_category(self, category):
        return [b for b in self.bookmarks.values() if b.category == category]
    
    def get_most_visited(self, limit=10):
        sorted_bookmarks = sorted(
            self.bookmarks.values(),
            key=lambda b: b.visit_count,
            reverse=True
        )
        return sorted_bookmarks[:limit]
    
    def get_recent(self, limit=10):
        sorted_bookmarks = sorted(
            self.bookmarks.values(),
            key=lambda b: b.created_at,
            reverse=True
        )
        return sorted_bookmarks[:limit]
    
    def list_categories(self):
        return sorted(self.categories)
    
    def get_stats(self):
        return {
            'total': len(self.bookmarks),
            'categories': len(self.categories),
            'most_visited': [b.title for b in self.get_most_visited(5)]
        }

def main():
    manager = BookmarkManager()
    
    manager.add("https://www.python.org", "Python官网", "编程", "Python官方文档")
    manager.add("https://github.com", "GitHub", "编程", "代码托管平台")
    manager.add("https://www.google.com", "Google", "搜索", "搜索引擎")
    
    print("所有书签:")
    for bookmark in manager.bookmarks.values():
        print(f"  [{bookmark.id}] {bookmark.title}: {bookmark.url}")
    
    print("\n分类列表:", manager.list_categories())
    print("\n统计:", manager.get_stats())


if __name__ == "__main__":
    main()
