# -----------------------------
# 题目：装饰器模式实现咖啡订单系统。
# -----------------------------

class Beverage:
    def get_description(self):
        pass
    
    def get_cost(self):
        pass

class Espresso(Beverage):
    def get_description(self):
        return "浓缩咖啡"
    
    def get_cost(self):
        return 15.0

class HouseBlend(Beverage):
    def get_description(self):
        return "混合咖啡"
    
    def get_cost(self):
        return 12.0

class DarkRoast(Beverage):
    def get_description(self):
        return "深度烘焙咖啡"
    
    def get_cost(self):
        return 14.0

class Decaf(Beverage):
    def get_description(self):
        return "低咖啡因咖啡"
    
    def get_cost(self):
        return 13.0

class CondimentDecorator(Beverage):
    def __init__(self, beverage):
        self.beverage = beverage
    
    def get_description(self):
        return self.beverage.get_description()
    
    def get_cost(self):
        return self.beverage.get_cost()

class Milk(CondimentDecorator):
    def get_description(self):
        return f"{self.beverage.get_description()}, 加奶"
    
    def get_cost(self):
        return self.beverage.get_cost() + 3.0

class Mocha(CondimentDecorator):
    def get_description(self):
        return f"{self.beverage.get_description()}, 加摩卡"
    
    def get_cost(self):
        return self.beverage.get_cost() + 5.0

class Whip(CondimentDecorator):
    def get_description(self):
        return f"{self.beverage.get_description()}, 加奶油"
    
    def get_cost(self):
        return self.beverage.get_cost() + 4.0

class Soy(CondimentDecorator):
    def get_description(self):
        return f"{self.beverage.get_description()}, 加豆浆"
    
    def get_cost(self):
        return self.beverage.get_cost() + 3.5

class Caramel(CondimentDecorator):
    def get_description(self):
        return f"{self.beverage.get_description()}, 加焦糖"
    
    def get_cost(self):
        return self.beverage.get_cost() + 4.5

class CoffeeOrder:
    def __init__(self):
        self.items = []
    
    def add_beverage(self, beverage):
        self.items.append(beverage)
    
    def get_total(self):
        return sum(item.get_cost() for item in self.items)
    
    def print_order(self):
        print("=== 订单详情 ===")
        for i, item in enumerate(self.items, 1):
            print(f"{i}. {item.get_description()} - ¥{item.get_cost():.2f}")
        print(f"总计: ¥{self.get_total():.2f}")

def main():
    order = CoffeeOrder()
    
    beverage1 = Espresso()
    beverage1 = Milk(beverage1)
    beverage1 = Mocha(beverage1)
    order.add_beverage(beverage1)
    
    beverage2 = DarkRoast()
    beverage2 = Mocha(beverage2)
    beverage2 = Mocha(beverage2)
    beverage2 = Whip(beverage2)
    order.add_beverage(beverage2)
    
    beverage3 = HouseBlend()
    beverage3 = Soy(beverage3)
    beverage3 = Mocha(beverage3)
    beverage3 = Whip(beverage3)
    beverage3 = Caramel(beverage3)
    order.add_beverage(beverage3)
    
    order.print_order()


if __name__ == "__main__":
    main()
