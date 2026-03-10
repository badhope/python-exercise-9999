# -----------------------------
# 题目：实现简易搜索引擎。
# -----------------------------

import re
from collections import defaultdict

class SimpleSearchEngine:
    def __init__(self):
        self.index = defaultdict(list)
        self.documents = {}
    
    def add_document(self, doc_id, content):
        self.documents[doc_id] = content
        words = re.findall(r'\w+', content.lower())
        for word in set(words):
            self.index[word].append(doc_id)
    
    def search(self, query):
        words = re.findall(r'\w+', query.lower())
        if not words:
            return []
        results = set(self.index.get(words[0], []))
        for word in words[1:]:
            results &= set(self.index.get(word, []))
        return list(results)
    
    def get_document(self, doc_id):
        return self.documents.get(doc_id)

def main():
    engine = SimpleSearchEngine()
    engine.add_document(1, "Python 是一种高级编程语言")
    engine.add_document(2, "Java 是一种面向对象编程语言")
    engine.add_document(3, "Python 适合数据分析")
    engine.add_document(4, "机器学习是人工智能的分支")
    results = engine.search("Python")
    print(f"搜索 'Python' 结果: {results}")
    for doc_id in results:
        print(f"  文档{doc_id}: {engine.get_document(doc_id)}")


if __name__ == "__main__":
    main()
