# -----------------------------
# 题目：实现简单的电商系统。
# 描述：管理商品、购物车、订单、支付等。
# -----------------------------

from datetime import datetime
from enum import Enum

class OrderStatus(Enum):
    PENDING = "待付款"
    PAID = "已付款"
    SHIPPED = "已发货"
    DELIVERED = "已送达"
    CANCELLED = "已取消"

class Product:
    def __init__(self, product_id, name, price, stock, category):
        self.id = product_id
        self.name = name
        self.price = price
        self.stock = stock
        self.category = category
        self.sales = 0
        self.is_active = True

class CartItem:
    def __init__(self, product, quantity):
        self.product = product
        self.quantity = quantity
    
    def get_subtotal(self):
        return self.product.price * self.quantity

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

class Order:
    def __init__(self, order_id, user_id, items, address):
        self.id = order_id
        self.user_id = user_id
        self.items = items
        self.address = address
        self.status = OrderStatus.PENDING
        self.total = sum(item.get_subtotal() for item in items.values())
        self.created_at = datetime.now()
        self.paid_at = None
        self.shipped_at = None
    
    def pay(self):
        if self.status == OrderStatus.PENDING:
            self.status = OrderStatus.PAID
            self.paid_at = datetime.now()
            return True
        return False
    
    def ship(self):
        if self.status == OrderStatus.PAID:
            self.status = OrderStatus.SHIPPED
            self.shipped_at = datetime.now()
            return True
        return False
    
    def deliver(self):
        if self.status == OrderStatus.SHIPPED:
            self.status = OrderStatus.DELIVERED
            return True
        return False
    
    def cancel(self):
        if self.status in [OrderStatus.PENDING, OrderStatus.PAID]:
            self.status = OrderStatus.CANCELLED
            return True
        return False

class ECommerceSystem:
    def __init__(self):
        self.products = {}
        self.carts = {}
        self.orders = {}
        self.next_product_id = 1
        self.next_order_id = 1
    
    def add_product(self, name, price, stock, category):
        product = Product(self.next_product_id, name, price, stock, category)
        self.products[self.next_product_id] = product
        self.next_product_id += 1
        return product.id
    
    def get_cart(self, user_id):
        if user_id not in self.carts:
            self.carts[user_id] = ShoppingCart()
        return self.carts[user_id]
    
    def add_to_cart(self, user_id, product_id, quantity=1):
        product = self.products.get(product_id)
        if product and product.stock >= quantity:
            cart = self.get_cart(user_id)
            cart.add_item(product, quantity)
            return True
        return False
    
    def create_order(self, user_id, address):
        cart = self.get_cart(user_id)
        if not cart.items:
            return None
        
        for item in cart.items.values():
            if item.product.stock < item.quantity:
                return None
        
        for item in cart.items.values():
            item.product.stock -= item.quantity
            item.product.sales += item.quantity
        
        order = Order(self.next_order_id, user_id, dict(cart.items), address)
        self.orders[self.next_order_id] = order
        self.next_order_id += 1
        
        cart.clear()
        return order.id
    
    def pay_order(self, order_id):
        order = self.orders.get(order_id)
        if order:
            return order.pay()
        return False
    
    def ship_order(self, order_id):
        order = self.orders.get(order_id)
        if order:
            return order.ship()
        return False
    
    def get_user_orders(self, user_id):
        return [o for o in self.orders.values() if o.user_id == user_id]
    
    def get_hot_products(self, limit=10):
        products = list(self.products.values())
        products.sort(key=lambda x: x.sales, reverse=True)
        return products[:limit]
    
    def search_products(self, keyword):
        keyword = keyword.lower()
        return [p for p in self.products.values() 
                if keyword in p.name.lower() or keyword in p.category.lower()]
    
    def get_stats(self):
        return {
            'products': len(self.products),
            'orders': len(self.orders),
            'total_sales': sum(p.sales for p in self.products.values()),
            'revenue': sum(o.total for o in self.orders.values() 
                          if o.status != OrderStatus.CANCELLED)
        }

def main():
    shop = ECommerceSystem()
    
    p1 = shop.add_product("iPhone 15", 6999, 100, "手机")
    p2 = shop.add_product("MacBook Pro", 12999, 50, "电脑")
    p3 = shop.add_product("AirPods", 1299, 200, "配件")
    
    shop.add_to_cart("user001", p1, 1)
    shop.add_to_cart("user001", p3, 2)
    
    cart = shop.get_cart("user001")
    print(f"购物车: {cart.get_item_count()}件商品, 总价{cart.get_total()}元")
    
    order_id = shop.create_order("user001", "北京市海淀区")
    if order_id:
        shop.pay_order(order_id)
        shop.ship_order(order_id)
    
    print("\n电商系统统计:")
    stats = shop.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
