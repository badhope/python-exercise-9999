# -----------------------------
# 题目：迭代器模式实现自定义迭代器。
# -----------------------------

class MyIterator:
    def __init__(self, data):
        self.data = data
        self.index = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.index >= len(self.data):
            raise StopIteration
        result = self.data[self.index]
        self.index += 1
        return result

class FibonacciIterator:
    def __init__(self, n):
        self.n = n
        self.current = 0
        self.a, self.b = 0, 1
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.current >= self.n:
            raise StopIteration
        result = self.a
        self.a, self.b = self.b, self.a + self.b
        self.current += 1
        return result

def main():
    print("遍历列表:")
    for item in MyIterator([1, 2, 3, 4, 5]):
        print(item, end=" ")
    print("\n斐波那契数列:")
    for num in FibonacciIterator(10):
        print(num, end=" ")
    print()


if __name__ == "__main__":
    main()
