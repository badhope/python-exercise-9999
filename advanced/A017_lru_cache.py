# -----------------------------
# 题目：实现LRU缓存。
# -----------------------------

from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity=128):
        self.cache = OrderedDict()
        self.capacity = capacity
    
    def get(self, key):
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        return None
    
    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
    
    def __contains__(self, key):
        return key in self.cache
    
    def __len__(self):
        return len(self.cache)

def main():
    cache = LRUCache(3)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("c", 3)
    print(f"获取a: {cache.get('a')}")
    cache.put("d", 4)
    print(f"获取a: {cache.get('a')}")
    print(f"获取b: {cache.get('b')}")


if __name__ == "__main__":
    main()
