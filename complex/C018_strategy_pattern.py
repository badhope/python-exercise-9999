# -----------------------------
# 题目：策略模式实现排序算法选择。
# -----------------------------

class SortStrategy:
    def sort(self, data):
        pass

class BubbleSort(SortStrategy):
    def sort(self, data):
        lst = data.copy()
        n = len(lst)
        for i in range(n):
            for j in range(0, n-i-1):
                if lst[j] > lst[j+1]:
                    lst[j], lst[j+1] = lst[j+1], lst[j]
        return lst

class QuickSort(SortStrategy):
    def sort(self, data):
        if len(data) <= 1:
            return data.copy()
        pivot = data[len(data) // 2]
        left = [x for x in data if x < pivot]
        middle = [x for x in data if x == pivot]
        right = [x for x in data if x > pivot]
        return self.sort(left) + middle + self.sort(right)

class Sorter:
    def __init__(self, strategy):
        self.strategy = strategy
    
    def set_strategy(self, strategy):
        self.strategy = strategy
    
    def sort(self, data):
        return self.strategy.sort(data)

def main():
    data = [64, 34, 25, 12, 22, 11, 90]
    sorter = Sorter(BubbleSort())
    print(f"原始数据: {data}")
    print(f"冒泡排序: {sorter.sort(data)}")
    sorter.set_strategy(QuickSort())
    print(f"快速排序: {sorter.sort(data)}")


if __name__ == "__main__":
    main()
