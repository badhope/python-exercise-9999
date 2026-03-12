# -----------------------------
# 题目：实现策略模式高级版。
# -----------------------------

from typing import Dict, Type, Any, Callable, List, Optional
from dataclasses import dataclass
from enum import Enum

class StrategyType(Enum):
    SORTING = "sorting"
    PRICING = "pricing"
    PAYMENT = "payment"
    SHIPPING = "shipping"

@dataclass
class StrategyInfo:
    name: str
    type: StrategyType
    description: str
    priority: int = 0

class Strategy:
    def __init__(self, info: StrategyInfo, execute: Callable):
        self.info = info
        self.execute = execute

class StrategyRegistry:
    _strategies: Dict[StrategyType, Dict[str, Strategy]] = {}
    
    @classmethod
    def register(cls, strategy_type: StrategyType, name: str, 
                 execute: Callable, description: str = "", priority: int = 0):
        if strategy_type not in cls._strategies:
            cls._strategies[strategy_type] = {}
        
        info = StrategyInfo(name, strategy_type, description, priority)
        cls._strategies[strategy_type][name] = Strategy(info, execute)
    
    @classmethod
    def get(cls, strategy_type: StrategyType, name: str) -> Optional[Strategy]:
        return cls._strategies.get(strategy_type, {}).get(name)
    
    @classmethod
    def get_all(cls, strategy_type: StrategyType) -> List[Strategy]:
        strategies = list(cls._strategies.get(strategy_type, {}).values())
        return sorted(strategies, key=lambda s: s.info.priority, reverse=True)
    
    @classmethod
    def get_names(cls, strategy_type: StrategyType) -> List[str]:
        return list(cls._strategies.get(strategy_type, {}).keys())

def strategy(strategy_type: StrategyType, name: str, description: str = "", priority: int = 0):
    def decorator(func: Callable) -> Callable:
        StrategyRegistry.register(strategy_type, name, func, description, priority)
        return func
    return decorator

class StrategyContext:
    def __init__(self, strategy_type: StrategyType):
        self.strategy_type = strategy_type
        self._current_strategy: Optional[Strategy] = None
    
    def use(self, name: str) -> 'StrategyContext':
        self._current_strategy = StrategyRegistry.get(self.strategy_type, name)
        return self
    
    def execute(self, *args, **kwargs) -> Any:
        if self._current_strategy is None:
            raise ValueError("未选择策略")
        return self._current_strategy.execute(*args, **kwargs)

class StrategyFactory:
    @staticmethod
    def create_context(strategy_type: StrategyType) -> StrategyContext:
        return StrategyContext(strategy_type)

class CompositeStrategy:
    def __init__(self, strategy_type: StrategyType):
        self.strategy_type = strategy_type
        self._strategies: List[Strategy] = []
    
    def add(self, name: str) -> 'CompositeStrategy':
        strategy = StrategyRegistry.get(self.strategy_type, name)
        if strategy:
            self._strategies.append(strategy)
        return self
    
    def execute_all(self, *args, **kwargs) -> List[Any]:
        results = []
        for strategy in self._strategies:
            results.append(strategy.execute(*args, **kwargs))
        return results
    
    def execute_until_success(self, *args, **kwargs) -> Any:
        for strategy in self._strategies:
            try:
                result = strategy.execute(*args, **kwargs)
                if result:
                    return result
            except Exception:
                continue
        return None

class StrategyChain:
    def __init__(self):
        self._strategies: List[Strategy] = []
    
    def add(self, strategy: Strategy) -> 'StrategyChain':
        self._strategies.append(strategy)
        return self
    
    def execute(self, data: Any) -> Any:
        result = data
        for strategy in self._strategies:
            result = strategy.execute(result)
        return result

@strategy(StrategyType.SORTING, "bubble_sort", "冒泡排序", priority=1)
def bubble_sort(data: List) -> List:
    arr = data.copy()
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

@strategy(StrategyType.SORTING, "quick_sort", "快速排序", priority=2)
def quick_sort(data: List) -> List:
    if len(data) <= 1:
        return data
    pivot = data[len(data) // 2]
    left = [x for x in data if x < pivot]
    middle = [x for x in data if x == pivot]
    right = [x for x in data if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)

@strategy(StrategyType.PRICING, "normal", "普通定价")
def normal_pricing(base_price: float) -> float:
    return base_price

@strategy(StrategyType.PRICING, "vip", "VIP定价")
def vip_pricing(base_price: float) -> float:
    return base_price * 0.8

@strategy(StrategyType.PRICING, "premium", "高级会员定价")
def premium_pricing(base_price: float) -> float:
    return base_price * 0.7

def main():
    print("=== 排序策略 ===")
    data = [64, 34, 25, 12, 22, 11, 90]
    
    context = StrategyFactory.create_context(StrategyType.SORTING)
    
    context.use("bubble_sort")
    result = context.execute(data)
    print(f"冒泡排序: {result}")
    
    context.use("quick_sort")
    result = context.execute(data)
    print(f"快速排序: {result}")
    
    print("\n=== 定价策略 ===")
    base_price = 1000
    
    context = StrategyFactory.create_context(StrategyType.PRICING)
    
    context.use("normal")
    print(f"普通价格: {context.execute(base_price)}")
    
    context.use("vip")
    print(f"VIP价格: {context.execute(base_price)}")
    
    context.use("premium")
    print(f"高级会员价格: {context.execute(base_price)}")
    
    print("\n=== 可用策略 ===")
    print(f"排序策略: {StrategyRegistry.get_names(StrategyType.SORTING)}")
    print(f"定价策略: {StrategyRegistry.get_names(StrategyType.PRICING)}")
    
    print("\n=== 组合策略 ===")
    composite = (CompositeStrategy(StrategyType.PRICING)
                 .add("normal")
                 .add("vip")
                 .add("premium"))
    
    results = composite.execute_all(base_price)
    print(f"所有定价结果: {results}")


if __name__ == "__main__":
    main()
