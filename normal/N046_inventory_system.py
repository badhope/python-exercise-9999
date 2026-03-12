# -----------------------------
# 题目：实现简单的库存管理系统。
# 描述：管理商品库存，支持入库出库。
# -----------------------------

from datetime import datetime

class Product:
    def __init__(self, product_id, name, price, quantity=0):
        self.id = product_id
        self.name = name
        self.price = price
        self.quantity = quantity
        self.min_stock = 10
        self.created_at = datetime.now()
    
    def get_value(self):
        return self.price * self.quantity
    
    def is_low_stock(self):
        return self.quantity < self.min_stock

class InventorySystem:
    def __init__(self):
        self.products = {}
        self.transactions = []
        self.next_product_id = 1
    
    def add_product(self, name, price, quantity=0):
        product = Product(self.next_product_id, name, price, quantity)
        self.products[self.next_product_id] = product
        self.next_product_id += 1
        return product.id
    
    def get_product(self, product_id):
        return self.products.get(product_id)
    
    def stock_in(self, product_id, quantity, note=""):
        product = self.products.get(product_id)
        if product and quantity > 0:
            product.quantity += quantity
            self.transactions.append({
                'type': 'in',
                'product_id': product_id,
                'product_name': product.name,
                'quantity': quantity,
                'note': note,
                'time': datetime.now()
            })
            return True
        return False
    
    def stock_out(self, product_id, quantity, note=""):
        product = self.products.get(product_id)
        if product and quantity > 0 and product.quantity >= quantity:
            product.quantity -= quantity
            self.transactions.append({
                'type': 'out',
                'product_id': product_id,
                'product_name': product.name,
                'quantity': quantity,
                'note': note,
                'time': datetime.now()
            })
            return True
        return False
    
    def get_low_stock_products(self):
        return [p for p in self.products.values() if p.is_low_stock()]
    
    def get_total_value(self):
        return sum(p.get_value() for p in self.products.values())
    
    def search(self, keyword):
        keyword = keyword.lower()
        return [p for p in self.products.values() if keyword in p.name.lower()]
    
    def get_transactions(self, product_id=None):
        if product_id:
            return [t for t in self.transactions if t['product_id'] == product_id]
        return self.transactions
    
    def get_stats(self):
        return {
            'total_products': len(self.products),
            'total_quantity': sum(p.quantity for p in self.products.values()),
            'total_value': self.get_total_value(),
            'low_stock_count': len(self.get_low_stock_products())
        }
    
    def list_products(self, sort_by='name'):
        products = list(self.products.values())
        if sort_by == 'name':
            products.sort(key=lambda p: p.name)
        elif sort_by == 'quantity':
            products.sort(key=lambda p: p.quantity, reverse=True)
        elif sort_by == 'value':
            products.sort(key=lambda p: p.get_value(), reverse=True)
        return products

def main():
    inventory = InventorySystem()
    
    p1 = inventory.add_product("笔记本", 5000, 20)
    p2 = inventory.add_product("鼠标", 50, 100)
    p3 = inventory.add_product("键盘", 200, 30)
    
    inventory.stock_in(p1, 10, "采购入库")
    inventory.stock_out(p2, 20, "销售出库")
    
    print("库存统计:")
    stats = inventory.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n所有商品:")
    for product in inventory.list_products():
        status = "⚠️低库存" if product.is_low_stock() else ""
        print(f"  {product.name}: {product.quantity}个, 单价{product.price}元 {status}")


if __name__ == "__main__":
    main()
