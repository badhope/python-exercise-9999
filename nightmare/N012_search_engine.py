# -----------------------------
# 题目：实现简单的分布式搜索引擎。
# 描述：支持索引、搜索、排序。
# -----------------------------

import re
from collections import defaultdict
import math

class Document:
    def __init__(self, doc_id, title, content):
        self.doc_id = doc_id
        self.title = title
        self.content = content
    
    def get_text(self):
        return f"{self.title} {self.content}"

class InvertedIndex:
    def __init__(self):
        self.index = defaultdict(list)
        self.documents = {}
        self.doc_lengths = defaultdict(float)
        self.term_freq = defaultdict(lambda: defaultdict(int))
    
    def _tokenize(self, text):
        text = text.lower()
        tokens = re.findall(r'\w+', text)
        return tokens
    
    def add_document(self, doc):
        self.documents[doc.doc_id] = doc
        tokens = self._tokenize(doc.get_text())
        
        term_count = defaultdict(int)
        for token in tokens:
            term_count[token] += 1
            self.term_freq[doc.doc_id][token] += 1
        
        for token, count in term_count.items():
            self.index[token].append(doc.doc_id)
        
        self.doc_lengths[doc.doc_id] = len(tokens)
    
    def search(self, query):
        tokens = self._tokenize(query)
        if not tokens:
            return []
        
        doc_scores = defaultdict(float)
        
        for token in tokens:
            if token in self.index:
                idf = math.log(len(self.documents) / len(self.index[token]) + 1)
                for doc_id in self.index[token]:
                    tf = self.term_freq[doc_id][token]
                    tfidf = tf * idf
                    doc_scores[doc_id] += tfidf
        
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        return [(self.documents[doc_id], score) for doc_id, score in sorted_docs]

class SearchEngine:
    def __init__(self):
        self.index = InvertedIndex()
    
    def index_document(self, doc_id, title, content):
        doc = Document(doc_id, title, content)
        self.index.add_document(doc)
    
    def search(self, query, limit=10):
        results = self.index.search(query)
        return results[:limit]
    
    def suggest(self, prefix):
        suggestions = []
        for term in self.index.index.keys():
            if term.startswith(prefix.lower()):
                suggestions.append(term)
        return suggestions[:5]

class DistributedSearchEngine:
    def __init__(self, num_shards=3):
        self.shards = [SearchEngine() for _ in range(num_shards)]
    
    def _get_shard(self, doc_id):
        return hash(doc_id) % len(self.shards)
    
    def index_document(self, doc_id, title, content):
        shard = self.shards[self._get_shard(doc_id)]
        shard.index_document(doc_id, title, content)
    
    def search(self, query, limit=10):
        all_results = []
        for shard in self.shards:
            results = shard.search(query, limit)
            all_results.extend(results)
        
        all_results.sort(key=lambda x: x[1], reverse=True)
        return all_results[:limit]

def main():
    engine = DistributedSearchEngine(3)
    
    engine.index_document(1, "Python编程入门", "Python是一门简单易学的编程语言")
    engine.index_document(2, "Java开发指南", "Java是面向对象的编程语言")
    engine.index_document(3, "Python数据分析", "使用Python进行数据分析和可视化")
    engine.index_document(4, "Web开发教程", "Python Django框架开发Web应用")
    engine.index_document(5, "机器学习入门", "Python机器学习算法实现")
    
    results = engine.search("Python")
    print("搜索 'Python':")
    for doc, score in results:
        print(f"  [{score:.2f}] {doc.title}: {doc.content}")


if __name__ == "__main__":
    main()
