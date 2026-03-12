# -----------------------------
# 题目：实现超市收银系统。
# 描述：管理商品、购物车、结算等功能。
# -----------------------------

from datetime import datetime

class Product:
    def __init__(self, product_id, name, price, barcode, stock):
        self.id = product_id
        self.name = name
        self.price = price
        self.barcode = barcode
        self.stock = stock
        self.discount = 1.0

class CartItem:
    def __init__(self, product, quantity):
        self.product = product
        self.quantity = quantity
    
    def get_subtotal(self):
        return self.product.price * self.product.discount * self.quantity

class ShoppingCart:
    def __init__(self):
        self.items = {}
    
    def add_item(self, product, quantity=1):
        if product.id in self.items:
            self.items[product.id].quantity += quantity
        else:
            self.items[product.id] = CartItem(product, quantity)
    
    def remove_item(self, product_id):
        if product_id in self.items:
            del self.items[product_id]
    
    def update_quantity(self, product_id, quantity):
        if product_id in self.items:
            if quantity <= 0:
                self.remove_item(product_id)
            else:
                self.items[product_id].quantity = quantity
    
    def get_total(self):
        return sum(item.get_subtotal() for item in self.items.values())
    
    def get_item_count(self):
        return sum(item.quantity for item in self.items.values())
    
    def clear(self):
        self.items.clear()

class Receipt:
    def __init__(self, receipt_id, items, total, payment_method):
        self.id = receipt_id
        self.items = items
        self.total = total
        self.payment_method = payment_method
        self.time = datetime.now()

class SupermarketSystem:
    def __init__(self):
        self.products = {}
        self.carts = {}
        self.receipts = {}
        self.next_product_id = 1
        self.next_receipt_id = 1
    
    def add_product(self, name, price, barcode, stock):
        product = Product(self.next_product_id, name, price, barcode, stock)
        self.products[self.next_product_id] = product
        self.next_product_id += 1
        return product.id
    
    def get_product_by_barcode(self, barcode):
        for product in self.products.values():
            if product.barcode == barcode:
                return product
        return None
    
    def create_cart(self, cart_id):
        self.carts[cart_id] = ShoppingCart()
        return cart_id
    
    def scan_product(self, cart_id, barcode, quantity=1):
        cart = self.carts.get(cart_id)
        product = self.get_product_by_barcode(barcode)
        
        if not cart or not product:
            return False, "购物车或商品不存在"
        
        if product.stock < quantity:
            return False, "库存不足"
        
        cart.add_item(product, quantity)
        return True, f"已添加: {product.name} x{quantity}"
    
    def checkout(self, cart_id, payment_method="cash"):
        cart = self.carts.get(cart_id)
        if not cart or not cart.items:
            return None, "购物车为空"
        
        for item in cart.items.values():
            if item.product.stock < item.quantity:
                return None, f"{item.product.name}库存不足"
        
        for item in cart.items.values():
            item.product.stock -= item.quantity
        
        items = [(item.product.name, item.quantity, item.get_subtotal()) 
                for item in cart.items.values()]
        total = cart.get_total()
        
        receipt = Receipt(self.next_receipt_id, items, total, payment_method)
        self.receipts[self.next_receipt_id] = receipt
        self.next_receipt_id += 1
        
        cart.clear()
        
        return receipt.id, f"结算成功，总计: {total:.2f}元"
    
    def set_discount(self, product_id, discount):
        product = self.products.get(product_id)
        if product:
            product.discount = discount
            return True
        return False
    
    def get_low_stock_products(self, threshold=10):
        return [p for p in self.products.values() if p.stock < threshold]
    
    def get_sales_report(self):
        total_sales = sum(r.total for r in self.receipts.values())
        total_transactions = len(self.receipts)
        
        return {
            'total_sales': total_sales,
            'total_transactions': total_transactions,
            'average_transaction': total_sales / total_transactions if total_transactions > 0 else 0
        }
    
    def get_stats(self):
        return {
            'products': len(self.products),
            'active_carts': len([c for c in self.carts.values() if c.items]),
            'total_receipts': len(self.receipts),
            'low_stock': len(self.get_low_stock_products())
        }

def main():
    supermarket = SupermarketSystem()
    
    supermarket.add_product("苹果", 5.5, "6901234567890", 100)
    supermarket.add_product("牛奶", 6.0, "6901234567891", 50)
    supermarket.add_product("面包", 8.0, "6901234567892", 30)
    
    cart_id = supermarket.create_cart("cart001")
    
    supermarket.scan_product(cart_id, "6901234567890", 3)
    supermarket.scan_product(cart_id, "6901234567891", 2)
    supermarket.scan_product(cart_id, "6901234567892", 1)
    
    print("超市统计:")
    stats = supermarket.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    cart = supermarket.carts[cart_id]
    print(f"\n购物车商品数: {cart.get_item_count()}")
    print(f"购物车总计: {cart.get_total():.2f}元")
    
    receipt_id, msg = supermarket.checkout(cart_id)
    print(f"\n{msg}")


if __name__ == "__main__":
    main()
