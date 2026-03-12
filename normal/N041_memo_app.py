# -----------------------------
# 题目：实现简单的备忘录。
# 描述：支持添加、删除、搜索备忘录。
# -----------------------------

from datetime import datetime

class Memo:
    def __init__(self, memo_id, title, content, tags=None):
        self.id = memo_id
        self.title = title
        self.content = content
        self.tags = tags or []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def update(self, title=None, content=None, tags=None):
        if title:
            self.title = title
        if content:
            self.content = content
        if tags is not None:
            self.tags = tags
        self.updated_at = datetime.now()
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'tags': self.tags,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class MemoApp:
    def __init__(self):
        self.memos = {}
        self.next_id = 1
    
    def add(self, title, content, tags=None):
        memo = Memo(self.next_id, title, content, tags)
        self.memos[self.next_id] = memo
        self.next_id += 1
        return memo.id
    
    def get(self, memo_id):
        return self.memos.get(memo_id)
    
    def update(self, memo_id, **kwargs):
        memo = self.memos.get(memo_id)
        if memo:
            memo.update(**kwargs)
            return True
        return False
    
    def delete(self, memo_id):
        if memo_id in self.memos:
            del self.memos[memo_id]
            return True
        return False
    
    def search(self, keyword):
        results = []
        keyword = keyword.lower()
        for memo in self.memos.values():
            if (keyword in memo.title.lower() or 
                keyword in memo.content.lower() or
                any(keyword in tag.lower() for tag in memo.tags)):
                results.append(memo)
        return results
    
    def search_by_tag(self, tag):
        results = []
        tag = tag.lower()
        for memo in self.memos.values():
            if any(tag == t.lower() for t in memo.tags):
                results.append(memo)
        return results
    
    def list_all(self):
        return sorted(self.memos.values(), key=lambda m: m.updated_at, reverse=True)
    
    def get_stats(self):
        all_tags = set()
        for memo in self.memos.values():
            all_tags.update(memo.tags)
        return {
            'total': len(self.memos),
            'tags': sorted(all_tags)
        }

def main():
    app = MemoApp()
    
    app.add("学习计划", "学习Python和算法", ["学习", "编程"])
    app.add("购物清单", "牛奶、面包、鸡蛋", ["生活"])
    app.add("工作笔记", "完成项目报告", ["工作", "重要"])
    
    print("所有备忘录:")
    for memo in app.list_all():
        print(f"  [{memo.id}] {memo.title}: {memo.content[:20]}...")
    
    print("\n搜索'学习':")
    results = app.search("学习")
    for memo in results:
        print(f"  {memo.title}")
    
    print(f"\n统计: {app.get_stats()}")


if __name__ == "__main__":
    main()
