# -----------------------------
# 题目：实现商品库存管理系统。
# 描述：管理商品、库存、入库出库、预警等。
# -----------------------------

from datetime import datetime

class Product:
    def __init__(self, product_id, name, category, price, unit):
        self.id = product_id
        self.name = name
        self.category = category
        self.price = price
        self.unit = unit
        self.stock = 0
        self.min_stock = 10
        self.max_stock = 100

class StockRecord:
    def __init__(self, record_id, product_id, quantity, record_type, operator):
        self.id = record_id
        self.product_id = product_id
        self.quantity = quantity
        self.type = record_type
        self.operator = operator
        self.time = datetime.now()

class InventorySystem:
    def __init__(self):
        self.products = {}
        self.records = []
        self.next_product_id = 1
        self.next_record_id = 1
    
    def add_product(self, name, category, price, unit, min_stock=10, max_stock=100):
        product = Product(self.next_product_id, name, category, price, unit)
        product.min_stock = min_stock
        product.max_stock = max_stock
        self.products[self.next_product_id] = product
        self.next_product_id += 1
        return product.id
    
    def stock_in(self, product_id, quantity, operator):
        product = self.products.get(product_id)
        if product and quantity > 0:
            product.stock += quantity
            record = StockRecord(self.next_record_id, product_id, quantity, "入库", operator)
            self.records.append(record)
            self.next_record_id += 1
            return True, f"入库成功，当前库存: {product.stock}{product.unit}"
        return False, "入库失败"
    
    def stock_out(self, product_id, quantity, operator):
        product = self.products.get(product_id)
        if product and quantity > 0 and product.stock >= quantity:
            product.stock -= quantity
            record = StockRecord(self.next_record_id, product_id, quantity, "出库", operator)
            self.records.append(record)
            self.next_record_id += 1
            return True, f"出库成功，当前库存: {product.stock}{product.unit}"
        return False, "库存不足或商品不存在"
    
    def get_product_info(self, product_id):
        product = self.products.get(product_id)
        if product:
            return {
                'id': product.id,
                'name': product.name,
                'category': product.category,
                'price': product.price,
                'stock': product.stock,
                'unit': product.unit,
                'status': self._get_status(product)
            }
        return None
    
    def _get_status(self, product):
        if product.stock <= 0:
            return "缺货"
        elif product.stock < product.min_stock:
            return "低库存"
        elif product.stock > product.max_stock:
            return "超储"
        return "正常"
    
    def get_low_stock_products(self):
        return [p for p in self.products.values() if p.stock < p.min_stock]
    
    def get_overstock_products(self):
        return [p for p in self.products.values() if p.stock > p.max_stock]
    
    def get_out_of_stock_products(self):
        return [p for p in self.products.values() if p.stock <= 0]
    
    def get_product_records(self, product_id):
        return [r for r in self.records if r.product_id == product_id]
    
    def get_category_summary(self):
        summary = {}
        for product in self.products.values():
            if product.category not in summary:
                summary[product.category] = {'count': 0, 'value': 0}
            summary[product.category]['count'] += product.stock
            summary[product.category]['value'] += product.stock * product.price
        return summary
    
    def get_total_value(self):
        return sum(p.stock * p.price for p in self.products.values())
    
    def search_products(self, keyword):
        keyword = keyword.lower()
        return [p for p in self.products.values() 
                if keyword in p.name.lower() or keyword in p.category.lower()]
    
    def get_stats(self):
        return {
            'products': len(self.products),
            'total_stock': sum(p.stock for p in self.products.values()),
            'total_value': self.get_total_value(),
            'low_stock': len(self.get_low_stock_products()),
            'out_of_stock': len(self.get_out_stock_products()),
            'records': len(self.records)
        }

def main():
    inventory = InventorySystem()
    
    p1 = inventory.add_product("笔记本", "电子产品", 5000, "台", 5, 50)
    p2 = inventory.add_product("鼠标", "电子产品", 50, "个", 20, 200)
    p3 = inventory.add_product("键盘", "电子产品", 200, "个", 10, 100)
    
    inventory.stock_in(p1, 30, "管理员")
    inventory.stock_in(p2, 100, "管理员")
    inventory.stock_in(p3, 50, "管理员")
    
    inventory.stock_out(p1, 5, "销售员")
    inventory.stock_out(p2, 30, "销售员")
    
    print("库存统计:")
    stats = inventory.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n低库存商品:")
    for product in inventory.get_low_stock_products():
        print(f"  {product.name}: {product.stock}{product.unit}")
    
    print(f"\n库存总价值: {inventory.get_total_value()}元")


if __name__ == "__main__":
    main()
