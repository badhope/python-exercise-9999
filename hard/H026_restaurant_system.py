# -----------------------------
# 题目：实现餐厅点餐系统。
# 描述：管理菜单、订单、桌台等功能。
# -----------------------------

from datetime import datetime

class MenuItem:
    def __init__(self, item_id, name, price, category):
        self.id = item_id
        self.name = name
        self.price = price
        self.category = category
        self.is_available = True

class Table:
    def __init__(self, table_id, capacity):
        self.id = table_id
        self.capacity = capacity
        self.status = "available"
        self.current_order = None
        self.guests = 0
    
    def seat(self, guests):
        if self.status != "available":
            return False
        if guests > self.capacity:
            return False
        self.status = "occupied"
        self.guests = guests
        return True
    
    def vacate(self):
        self.status = "available"
        self.current_order = None
        self.guests = 0

class OrderItem:
    def __init__(self, menu_item, quantity, notes=""):
        self.menu_item = menu_item
        self.quantity = quantity
        self.notes = notes
        self.status = "pending"
    
    def get_subtotal(self):
        return self.menu_item.price * self.quantity

class Order:
    def __init__(self, order_id, table_id):
        self.id = order_id
        self.table_id = table_id
        self.items = []
        self.status = "active"
        self.created_at = datetime.now()
    
    def add_item(self, menu_item, quantity=1, notes=""):
        for item in self.items:
            if item.menu_item.id == menu_item.id and item.notes == notes:
                item.quantity += quantity
                return
        self.items.append(OrderItem(menu_item, quantity, notes))
    
    def remove_item(self, item_id):
        self.items = [item for item in self.items if item.menu_item.id != item_id]
    
    def get_total(self):
        return sum(item.get_subtotal() for item in self.items)
    
    def get_item_count(self):
        return sum(item.quantity for item in self.items)

class RestaurantSystem:
    def __init__(self):
        self.menu_items = {}
        self.tables = {}
        self.orders = {}
        self.next_menu_id = 1
        self.next_table_id = 1
        self.next_order_id = 1
    
    def add_menu_item(self, name, price, category):
        item = MenuItem(self.next_menu_id, name, price, category)
        self.menu_items[self.next_menu_id] = item
        self.next_menu_id += 1
        return item.id
    
    def add_table(self, capacity):
        table = Table(self.next_table_id, capacity)
        self.tables[self.next_table_id] = table
        self.next_table_id += 1
        return table.id
    
    def get_menu_by_category(self, category=None):
        if category:
            return [item for item in self.menu_items.values() 
                   if item.category == category and item.is_available]
        return [item for item in self.menu_items.values() if item.is_available]
    
    def seat_table(self, table_id, guests):
        table = self.tables.get(table_id)
        if table and table.seat(guests):
            order = Order(self.next_order_id, table_id)
            self.orders[self.next_order_id] = order
            table.current_order = order.id
            self.next_order_id += 1
            return order.id
        return None
    
    def add_order_item(self, table_id, menu_item_id, quantity=1, notes=""):
        table = self.tables.get(table_id)
        if not table or not table.current_order:
            return False
        
        order = self.orders.get(table.current_order)
        menu_item = self.menu_items.get(menu_item_id)
        
        if order and menu_item:
            order.add_item(menu_item, quantity, notes)
            return True
        return False
    
    def get_bill(self, table_id):
        table = self.tables.get(table_id)
        if table and table.current_order:
            order = self.orders.get(table.current_order)
            if order:
                return {
                    'order_id': order.id,
                    'items': [(item.menu_item.name, item.quantity, item.get_subtotal()) 
                             for item in order.items],
                    'total': order.get_total()
                }
        return None
    
    def checkout(self, table_id):
        table = self.tables.get(table_id)
        if table and table.current_order:
            order = self.orders.get(table.current_order)
            if order:
                total = order.get_total()
                order.status = "completed"
                table.vacate()
                return total
        return None
    
    def get_stats(self):
        total_tables = len(self.tables)
        occupied = sum(1 for t in self.tables.values() if t.status == "occupied")
        
        return {
            'total_tables': total_tables,
            'available_tables': total_tables - occupied,
            'occupied_tables': occupied,
            'menu_items': len(self.menu_items),
            'active_orders': sum(1 for o in self.orders.values() if o.status == "active")
        }

def main():
    restaurant = RestaurantSystem()
    
    restaurant.add_menu_item("红烧肉", 48, "热菜")
    restaurant.add_menu_item("宫保鸡丁", 38, "热菜")
    restaurant.add_menu_item("米饭", 3, "主食")
    restaurant.add_menu_item("可乐", 8, "饮料")
    
    t1 = restaurant.add_table(4)
    t2 = restaurant.add_table(6)
    
    order1 = restaurant.seat_table(t1, 3)
    restaurant.add_order_item(t1, 1, 1)
    restaurant.add_order_item(t1, 2, 1)
    restaurant.add_order_item(t1, 3, 3)
    
    print("餐厅统计:")
    stats = restaurant.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print(f"\n桌台{t1}账单:")
    bill = restaurant.get_bill(t1)
    for name, qty, subtotal in bill['items']:
        print(f"  {name} x{qty}: {subtotal}元")
    print(f"  总计: {bill['total']}元")


if __name__ == "__main__":
    main()
