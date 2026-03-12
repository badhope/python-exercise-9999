# -----------------------------
# 题目：实现分布式搜索引擎。
# 描述：支持索引分片、分布式查询、结果聚合。
# -----------------------------

import time
import threading
import hashlib
import re
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
from bisect import bisect_right

@dataclass
class Document:
    doc_id: str
    title: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

@dataclass
class IndexEntry:
    doc_id: str
    positions: List[int] = field(default_factory=list)
    tf: float = 0.0

@dataclass
class SearchResult:
    doc_id: str
    score: float
    title: str
    snippet: str
    highlight: str = ""

class InvertedIndex:
    def __init__(self):
        self.index: Dict[str, Dict[str, IndexEntry]] = defaultdict(lambda: defaultdict(IndexEntry))
        self.documents: Dict[str, Document] = {}
        self.doc_count = 0
        self._lock = threading.Lock()
    
    def tokenize(self, text: str) -> List[str]:
        text = text.lower()
        tokens = re.findall(r'\w+', text)
        return tokens
    
    def add_document(self, doc: Document):
        with self._lock:
            self.documents[doc.doc_id] = doc
            self.doc_count += 1
            
            tokens = self.tokenize(doc.title + " " + doc.content)
            
            term_freq: Dict[str, int] = defaultdict(int)
            
            for position, token in enumerate(tokens):
                term_freq[token] += 1
                
                if doc.doc_id not in self.index[token]:
                    self.index[token][doc.doc_id] = IndexEntry(doc_id=doc.doc_id)
                
                self.index[token][doc.doc_id].positions.append(position)
            
            for term, freq in term_freq.items():
                self.index[term][doc.doc_id].tf = freq / len(tokens)
    
    def remove_document(self, doc_id: str):
        with self._lock:
            if doc_id in self.documents:
                del self.documents[doc_id]
                self.doc_count -= 1
                
                for term in list(self.index.keys()):
                    if doc_id in self.index[term]:
                        del self.index[term][doc_id]
    
    def search(self, query: str, limit: int = 10) -> List[Tuple[str, float]]:
        tokens = self.tokenize(query)
        
        scores: Dict[str, float] = defaultdict(float)
        
        for token in tokens:
            if token in self.index:
                df = len(self.index[token])
                idf = 1 + (self.doc_count / (df + 1))
                
                for doc_id, entry in self.index[token].items():
                    scores[doc_id] += entry.tf * idf
        
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_results[:limit]
    
    def get_document(self, doc_id: str) -> Optional[Document]:
        return self.documents.get(doc_id)

class IndexShard:
    def __init__(self, shard_id: int):
        self.shard_id = shard_id
        self.index = InvertedIndex()
    
    def add_document(self, doc: Document):
        self.index.add_document(doc)
    
    def search(self, query: str, limit: int = 10) -> List[Tuple[str, float]]:
        return self.index.search(query, limit)
    
    def get_document(self, doc_id: str) -> Optional[Document]:
        return self.index.get_document(doc_id)
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'shard_id': self.shard_id,
            'doc_count': self.index.doc_count,
            'term_count': len(self.index.index)
        }

class ShardRouter:
    def __init__(self, num_shards: int = 4):
        self.num_shards = num_shards
        self.shards: Dict[int, IndexShard] = {
            i: IndexShard(i) for i in range(num_shards)
        }
    
    def get_shard(self, doc_id: str) -> int:
        hash_val = int(hashlib.md5(doc_id.encode()).hexdigest(), 16)
        return hash_val % self.num_shards
    
    def get_all_shards(self) -> List[IndexShard]:
        return list(self.shards.values())

class DistributedSearchEngine:
    def __init__(self, num_shards: int = 4):
        self.router = ShardRouter(num_shards)
        self._doc_counter = 0
        self._lock = threading.Lock()
    
    def index_document(self, title: str, content: str, metadata: Dict = None) -> str:
        with self._lock:
            self._doc_counter += 1
            doc_id = f"doc-{int(time.time())}-{self._doc_counter}"
        
        doc = Document(
            doc_id=doc_id,
            title=title,
            content=content,
            metadata=metadata or {}
        )
        
        shard_id = self.router.get_shard(doc_id)
        self.router.shards[shard_id].add_document(doc)
        
        return doc_id
    
    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        all_results: Dict[str, float] = {}
        
        for shard in self.router.get_all_shards():
            results = shard.search(query, limit * 2)
            for doc_id, score in results:
                if doc_id not in all_results or all_results[doc_id] < score:
                    all_results[doc_id] = score
        
        sorted_results = sorted(all_results.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        search_results = []
        for doc_id, score in sorted_results:
            shard_id = self.router.get_shard(doc_id)
            doc = self.router.shards[shard_id].get_document(doc_id)
            
            if doc:
                snippet = doc.content[:100] + "..." if len(doc.content) > 100 else doc.content
                
                search_results.append(SearchResult(
                    doc_id=doc_id,
                    score=score,
                    title=doc.title,
                    snippet=snippet
                ))
        
        return search_results
    
    def get_document(self, doc_id: str) -> Optional[Document]:
        shard_id = self.router.get_shard(doc_id)
        return self.router.shards[shard_id].get_document(doc_id)
    
    def get_stats(self) -> Dict[str, Any]:
        shard_stats = [shard.get_stats() for shard in self.router.get_all_shards()]
        
        return {
            'num_shards': self.router.num_shards,
            'shards': shard_stats,
            'total_docs': sum(s['doc_count'] for s in shard_stats),
            'total_terms': sum(s['term_count'] for s in shard_stats)
        }

def main():
    engine = DistributedSearchEngine(num_shards=3)
    
    print("索引文档...")
    docs = [
        ("Python编程入门", "Python是一种流行的编程语言，适合初学者学习。"),
        ("Java开发指南", "Java是企业级应用开发的首选语言。"),
        ("Python数据分析", "使用Python进行数据分析，包括pandas和numpy库。"),
        ("Web开发基础", "学习HTML、CSS和JavaScript进行Web开发。"),
        ("Python机器学习", "Python在机器学习领域有广泛应用，如TensorFlow和PyTorch。"),
        ("数据库设计", "学习关系型数据库的设计原则和SQL查询。"),
        ("Python爬虫教程", "使用Python编写网络爬虫，抓取网页数据。"),
        ("分布式系统", "了解分布式系统的基本概念和设计模式。")
    ]
    
    for title, content in docs:
        doc_id = engine.index_document(title, content)
        print(f"  索引: {title} -> {doc_id}")
    
    print("\n搜索 'Python':")
    results = engine.search("Python")
    for r in results:
        print(f"  [{r.score:.2f}] {r.title}: {r.snippet}")
    
    print("\n搜索 '开发':")
    results = engine.search("开发")
    for r in results:
        print(f"  [{r.score:.2f}] {r.title}: {r.snippet}")
    
    print("\n引擎统计:")
    stats = engine.get_stats()
    print(f"  分片数: {stats['num_shards']}")
    print(f"  文档总数: {stats['total_docs']}")
    print(f"  词汇总数: {stats['total_terms']}")

if __name__ == "__main__":
    main()
