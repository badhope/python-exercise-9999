# -----------------------------
# 题目：库存管理系统。
# 描述：实现商品库存的入库、出库、查询功能。
# -----------------------------

class Product:
    def __init__(self, product_id, name, price):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.quantity = 0

class InventoryManager:
    def __init__(self):
        self.products = {}
    
    def add_product(self, product_id, name, price):
        self.products[product_id] = Product(product_id, name, price)
    
    def stock_in(self, product_id, quantity):
        if product_id in self.products:
            self.products[product_id].quantity += quantity
    
    def stock_out(self, product_id, quantity):
        if product_id in self.products:
            product = self.products[product_id]
            if product.quantity >= quantity:
                product.quantity -= quantity
                return True
        return False
    
    def get_product(self, product_id):
        return self.products.get(product_id)
    
    def get_total_value(self):
        return sum(p.price * p.quantity for p in self.products.values())
    
    def get_low_stock(self, threshold=10):
        return [p for p in self.products.values() if p.quantity < threshold]

def main():
    inventory = InventoryManager()
    inventory.add_product("P001", "笔记本", 5999)
    inventory.stock_in("P001", 50)
    inventory.stock_out("P001", 5)
    product = inventory.get_product("P001")
    print(f"{product.name} 库存: {product.quantity}, 总价值: {inventory.get_total_value()}")


if __name__ == "__main__":
    main()
