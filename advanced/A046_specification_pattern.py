# -----------------------------
# 题目：实现简单的规格模式。
# -----------------------------

from typing import TypeVar, Generic, Callable, List, Any
from abc import ABC, abstractmethod

T = TypeVar('T')

class Specification(ABC, Generic[T]):
    @abstractmethod
    def is_satisfied_by(self, candidate: T) -> bool:
        pass
    
    def and_(self, other: 'Specification[T]') -> 'Specification[T]':
        return AndSpecification(self, other)
    
    def or_(self, other: 'Specification[T]') -> 'Specification[T]':
        return OrSpecification(self, other)
    
    def not_(self) -> 'Specification[T]':
        return NotSpecification(self)

class AndSpecification(Specification[T]):
    def __init__(self, left: Specification[T], right: Specification[T]):
        self.left = left
        self.right = right
    
    def is_satisfied_by(self, candidate: T) -> bool:
        return self.left.is_satisfied_by(candidate) and self.right.is_satisfied_by(candidate)

class OrSpecification(Specification[T]):
    def __init__(self, left: Specification[T], right: Specification[T]):
        self.left = left
        self.right = right
    
    def is_satisfied_by(self, candidate: T) -> bool:
        return self.left.is_satisfied_by(candidate) or self.right.is_satisfied_by(candidate)

class NotSpecification(Specification[T]):
    def __init__(self, spec: Specification[T]):
        self.spec = spec
    
    def is_satisfied_by(self, candidate: T) -> bool:
        return not self.spec.is_satisfied_by(candidate)

class LambdaSpecification(Specification[T]):
    def __init__(self, predicate: Callable[[T], bool]):
        self.predicate = predicate
    
    def is_satisfied_by(self, candidate: T) -> bool:
        return self.predicate(candidate)

class SpecificationBuilder:
    def __init__(self):
        self._spec: Specification = None
    
    def where(self, predicate: Callable[[T], bool]) -> 'SpecificationBuilder':
        spec = LambdaSpecification(predicate)
        if self._spec is None:
            self._spec = spec
        else:
            self._spec = AndSpecification(self._spec, spec)
        return self
    
    def or_where(self, predicate: Callable[[T], bool]) -> 'SpecificationBuilder':
        spec = LambdaSpecification(predicate)
        if self._spec is None:
            self._spec = spec
        else:
            self._spec = OrSpecification(self._spec, spec)
        return self
    
    def build(self) -> Specification[T]:
        return self._spec

class Product:
    def __init__(self, name: str, price: float, category: str, in_stock: bool):
        self.name = name
        self.price = price
        self.category = category
        self.in_stock = in_stock
    
    def __repr__(self):
        return f"Product({self.name}, ${self.price}, {self.category})"

class PriceSpecification(Specification[Product]):
    def __init__(self, min_price: float = None, max_price: float = None):
        self.min_price = min_price
        self.max_price = max_price
    
    def is_satisfied_by(self, candidate: Product) -> bool:
        if self.min_price is not None and candidate.price < self.min_price:
            return False
        if self.max_price is not None and candidate.price > self.max_price:
            return False
        return True

class CategorySpecification(Specification[Product]):
    def __init__(self, category: str):
        self.category = category
    
    def is_satisfied_by(self, candidate: Product) -> bool:
        return candidate.category == self.category

class InStockSpecification(Specification[Product]):
    def is_satisfied_by(self, candidate: Product) -> bool:
        return candidate.in_stock

class ProductFilter:
    def __init__(self, products: List[Product]):
        self.products = products
    
    def filter(self, spec: Specification[Product]) -> List[Product]:
        return [p for p in self.products if spec.is_satisfied_by(p)]

def main():
    products = [
        Product("iPhone", 999, "electronics", True),
        Product("MacBook", 1999, "electronics", True),
        Product("T-Shirt", 29, "clothing", True),
        Product("Jeans", 79, "clothing", False),
        Product("Headphones", 199, "electronics", True),
        Product("Sneakers", 129, "footwear", True)
    ]
    
    filter = ProductFilter(products)
    
    print("=== 价格范围规格 ===")
    price_spec = PriceSpecification(min_price=100, max_price=500)
    results = filter.filter(price_spec)
    for p in results:
        print(f"  {p}")
    
    print("\n=== 组合规格 ===")
    electronics = CategorySpecification("electronics")
    in_stock = InStockSpecification()
    affordable = PriceSpecification(max_price=1500)
    
    combined = electronics.and_(in_stock).and_(affordable)
    results = filter.filter(combined)
    for p in results:
        print(f"  {p}")
    
    print("\n=== 使用Builder ===")
    spec = (SpecificationBuilder()
            .where(lambda p: p.price < 200)
            .or_where(lambda p: p.category == "electronics")
            .build())
    
    results = filter.filter(spec)
    for p in results:
        print(f"  {p}")
    
    print("\n=== 取反规格 ===")
    not_electronics = CategorySpecification("electronics").not_()
    results = filter.filter(not_electronics)
    for p in results:
        print(f"  {p}")


if __name__ == "__main__":
    main()
