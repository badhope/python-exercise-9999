# -----------------------------
# 题目：实现外卖订餐系统。
# 描述：管理餐厅、菜单、订单、配送等功能。
# -----------------------------

from datetime import datetime
from enum import Enum

class OrderStatus(Enum):
    PENDING = "待接单"
    ACCEPTED = "已接单"
    PREPARING = "制作中"
    READY = "待配送"
    DELIVERING = "配送中"
    COMPLETED = "已完成"
    CANCELLED = "已取消"

class Restaurant:
    def __init__(self, restaurant_id, name, address, phone):
        self.id = restaurant_id
        self.name = name
        self.address = address
        self.phone = phone
        self.menu = {}
        self.is_open = True
        self.rating = 5.0

class MenuItem:
    def __init__(self, item_id, name, price, description=""):
        self.id = item_id
        self.name = name
        self.price = price
        self.description = description
        self.is_available = True

class OrderItem:
    def __init__(self, menu_item, quantity, notes=""):
        self.menu_item = menu_item
        self.quantity = quantity
        self.notes = notes
    
    def get_subtotal(self):
        return self.menu_item.price * self.quantity

class Order:
    def __init__(self, order_id, user_id, restaurant_id, address):
        self.id = order_id
        self.user_id = user_id
        self.restaurant_id = restaurant_id
        self.address = address
        self.items = []
        self.status = OrderStatus.PENDING
        self.total = 0
        self.delivery_fee = 5
        self.created_at = datetime.now()
        self.rider_id = None
    
    def add_item(self, menu_item, quantity=1, notes=""):
        self.items.append(OrderItem(menu_item, quantity, notes))
        self._calculate_total()
    
    def _calculate_total(self):
        self.total = sum(item.get_subtotal() for item in self.items) + self.delivery_fee
    
    def get_subtotal(self):
        return sum(item.get_subtotal() for item in self.items)

class Rider:
    def __init__(self, rider_id, name, phone):
        self.id = rider_id
        self.name = name
        self.phone = phone
        self.status = "idle"
        self.current_order = None

class DeliverySystem:
    def __init__(self):
        self.restaurants = {}
        self.orders = {}
        self.riders = {}
        self.next_restaurant_id = 1
        self.next_order_id = 1
        self.next_rider_id = 1
    
    def add_restaurant(self, name, address, phone):
        restaurant = Restaurant(self.next_restaurant_id, name, address, phone)
        self.restaurants[self.next_restaurant_id] = restaurant
        self.next_restaurant_id += 1
        return restaurant.id
    
    def add_menu_item(self, restaurant_id, name, price, description=""):
        restaurant = self.restaurants.get(restaurant_id)
        if restaurant:
            item_id = len(restaurant.menu) + 1
            item = MenuItem(item_id, name, price, description)
            restaurant.menu[item_id] = item
            return item_id
        return None
    
    def add_rider(self, name, phone):
        rider = Rider(self.next_rider_id, name, phone)
        self.riders[self.next_rider_id] = rider
        self.next_rider_id += 1
        return rider.id
    
    def create_order(self, user_id, restaurant_id, address):
        restaurant = self.restaurants.get(restaurant_id)
        if not restaurant or not restaurant.is_open:
            return None
        
        order = Order(self.next_order_id, user_id, restaurant_id, address)
        self.orders[self.next_order_id] = order
        self.next_order_id += 1
        return order.id
    
    def add_order_item(self, order_id, menu_item_id, quantity=1, notes=""):
        order = self.orders.get(order_id)
        restaurant = self.restaurants.get(order.restaurant_id) if order else None
        
        if order and restaurant and menu_item_id in restaurant.menu:
            menu_item = restaurant.menu[menu_item_id]
            if menu_item.is_available:
                order.add_item(menu_item, quantity, notes)
                return True
        return False
    
    def update_order_status(self, order_id, status):
        order = self.orders.get(order_id)
        if order:
            order.status = status
            return True
        return False
    
    def assign_rider(self, order_id):
        order = self.orders.get(order_id)
        if not order:
            return False
        
        for rider in self.riders.values():
            if rider.status == "idle":
                rider.status = "busy"
                rider.current_order = order_id
                order.rider_id = rider.id
                return True
        return False
    
    def complete_order(self, order_id):
        order = self.orders.get(order_id)
        if order and order.rider_id:
            rider = self.riders.get(order.rider_id)
            if rider:
                rider.status = "idle"
                rider.current_order = None
            order.status = OrderStatus.COMPLETED
            return True
        return False
    
    def get_user_orders(self, user_id):
        return [o for o in self.orders.values() if o.user_id == user_id]
    
    def get_restaurant_orders(self, restaurant_id):
        return [o for o in self.orders.values() if o.restaurant_id == restaurant_id]
    
    def get_stats(self):
        return {
            'restaurants': len(self.restaurants),
            'orders': len(self.orders),
            'riders': len(self.riders),
            'active_orders': sum(1 for o in self.orders.values() 
                                if o.status != OrderStatus.COMPLETED 
                                and o.status != OrderStatus.CANCELLED)
        }

def main():
    system = DeliverySystem()
    
    r1 = system.add_restaurant("美味餐厅", "北京市朝阳区", "010-12345678")
    system.add_menu_item(r1, "宫保鸡丁", 38, "经典川菜")
    system.add_menu_item(r1, "鱼香肉丝", 35, "传统川菜")
    system.add_menu_item(r1, "米饭", 3, "东北大米")
    
    rider1 = system.add_rider("张骑手", "13800138000")
    
    order1 = system.create_order("user001", r1, "北京市海淀区")
    system.add_order_item(order1, 1, 1)
    system.add_order_item(order1, 2, 1)
    system.add_order_item(order1, 3, 2)
    
    system.update_order_status(order1, OrderStatus.ACCEPTED)
    system.assign_rider(order1)
    
    print("外卖系统统计:")
    stats = system.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    order = system.orders[order1]
    print(f"\n订单{order1}:")
    print(f"  状态: {order.status.value}")
    print(f"  商品小计: {order.get_subtotal():.2f}元")
    print(f"  配送费: {order.delivery_fee}元")
    print(f"  总计: {order.total:.2f}元")


if __name__ == "__main__":
    main()
