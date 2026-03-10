# -----------------------------
# 题目：迭代器协议。
# 描述：实现迭代器协议。
# -----------------------------

class Counter:
    def __init__(self, max):
        self.max = max
        self.current = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.current >= self.max:
            raise StopIteration
        self.current += 1
        return self.current - 1

def main():
    for i in Counter(5):
        print(i)


if __name__ == "__main__":
    main()
