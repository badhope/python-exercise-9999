# -----------------------------
# 题目：购物车系统。
# 描述：实现购物车功能，支持添加、删除、计算总价。
# -----------------------------

class ShoppingCart:
    def __init__(self):
        self.items = {}
    
    def add_item(self, name, price, quantity=1):
        if name in self.items:
            self.items[name]["quantity"] += quantity
        else:
            self.items[name] = {"price": price, "quantity": quantity}
    
    def remove_item(self, name):
        if name in self.items:
            del self.items[name]
    
    def get_total(self):
        return sum(item["price"] * item["quantity"] for item in self.items.values())

def main():
    cart = ShoppingCart()
    cart.add_item("苹果", 5.5, 3)
    cart.add_item("香蕉", 3.0, 2)
    print(f"购物车总价: {cart.get_total()}元")


if __name__ == "__main__":
    main()
