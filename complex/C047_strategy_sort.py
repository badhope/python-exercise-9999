# -----------------------------
# 题目：策略模式实现排序算法选择。
# -----------------------------

from abc import ABC, abstractmethod

class SortStrategy(ABC):
    @abstractmethod
    def sort(self, data):
        pass
    
    @abstractmethod
    def get_name(self):
        pass

class BubbleSortStrategy(SortStrategy):
    def sort(self, data):
        arr = data.copy()
        n = len(arr)
        for i in range(n):
            for j in range(0, n - i - 1):
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
        return arr
    
    def get_name(self):
        return "冒泡排序"

class QuickSortStrategy(SortStrategy):
    def sort(self, data):
        arr = data.copy()
        self._quick_sort(arr, 0, len(arr) - 1)
        return arr
    
    def _quick_sort(self, arr, low, high):
        if low < high:
            pi = self._partition(arr, low, high)
            self._quick_sort(arr, low, pi - 1)
            self._quick_sort(arr, pi + 1, high)
    
    def _partition(self, arr, low, high):
        pivot = arr[high]
        i = low - 1
        for j in range(low, high):
            if arr[j] < pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        return i + 1
    
    def get_name(self):
        return "快速排序"

class MergeSortStrategy(SortStrategy):
    def sort(self, data):
        if len(data) <= 1:
            return data.copy()
        
        mid = len(data) // 2
        left = self.sort(data[:mid])
        right = self.sort(data[mid:])
        
        return self._merge(left, right)
    
    def _merge(self, left, right):
        result = []
        i = j = 0
        
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        
        result.extend(left[i:])
        result.extend(right[j:])
        return result
    
    def get_name(self):
        return "归并排序"

class InsertionSortStrategy(SortStrategy):
    def sort(self, data):
        arr = data.copy()
        for i in range(1, len(arr)):
            key = arr[i]
            j = i - 1
            while j >= 0 and arr[j] > key:
                arr[j + 1] = arr[j]
                j -= 1
            arr[j + 1] = key
        return arr
    
    def get_name(self):
        return "插入排序"

class Sorter:
    def __init__(self, strategy=None):
        self.strategy = strategy
    
    def set_strategy(self, strategy):
        self.strategy = strategy
    
    def sort(self, data):
        if not self.strategy:
            return sorted(data)
        return self.strategy.sort(data)
    
    def get_strategy_name(self):
        return self.strategy.get_name() if self.strategy else "默认排序"

class SortContext:
    def __init__(self):
        self.strategies = {
            'bubble': BubbleSortStrategy(),
            'quick': QuickSortStrategy(),
            'merge': MergeSortStrategy(),
            'insertion': InsertionSortStrategy()
        }
        self.sorter = Sorter()
    
    def sort_with(self, strategy_name, data):
        strategy = self.strategies.get(strategy_name)
        if strategy:
            self.sorter.set_strategy(strategy)
            return self.sorter.sort(data)
        return sorted(data)
    
    def benchmark(self, data):
        import time
        results = {}
        
        for name, strategy in self.strategies.items():
            start = time.time()
            strategy.sort(data)
            elapsed = time.time() - start
            results[name] = elapsed
        
        return results

def main():
    data = [64, 34, 25, 12, 22, 11, 90, 45, 33, 78]
    
    context = SortContext()
    
    print("=== 原始数据 ===")
    print(data)
    
    print("\n=== 各排序算法结果 ===")
    for name in ['bubble', 'quick', 'merge', 'insertion']:
        result = context.sort_with(name, data)
        print(f"{context.strategies[name].get_name()}: {result}")
    
    print("\n=== 性能测试 ===")
    import random
    large_data = [random.randint(1, 10000) for _ in range(1000)]
    
    results = context.benchmark(large_data)
    for name, elapsed in sorted(results.items(), key=lambda x: x[1]):
        print(f"{context.strategies[name].get_name()}: {elapsed:.6f}秒")


if __name__ == "__main__":
    main()
