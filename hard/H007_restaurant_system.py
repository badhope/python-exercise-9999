# -----------------------------
# 题目：餐厅点餐系统。
# 描述：实现菜单管理、订单创建、结账功能。
# -----------------------------

class MenuItem:
    def __init__(self, item_id, name, price):
        self.item_id = item_id
        self.name = name
        self.price = price

class RestaurantOrder:
    def __init__(self, table_number):
        self.table_number = table_number
        self.items = []
        self.status = "进行中"
    
    def add_item(self, menu_item, quantity=1):
        self.items.append({"item": menu_item, "quantity": quantity})
    
    def get_total(self):
        return sum(item["item"].price * item["quantity"] for item in self.items)
    
    def checkout(self):
        self.status = "已结账"
        return self.get_total()

class Restaurant:
    def __init__(self):
        self.menu = {}
        self.orders = {}
    
    def add_menu_item(self, item_id, name, price):
        self.menu[item_id] = MenuItem(item_id, name, price)
    
    def create_order(self, table_number):
        self.orders[table_number] = RestaurantOrder(table_number)
        return self.orders[table_number]
    
    def get_menu(self):
        return list(self.menu.values())

def main():
    restaurant = Restaurant()
    restaurant.add_menu_item("M001", "宫保鸡丁", 38)
    restaurant.add_menu_item("M002", "鱼香肉丝", 32)
    order = restaurant.create_order(1)
    order.add_item(restaurant.menu["M001"], 2)
    order.add_item(restaurant.menu["M002"], 1)
    print(f"桌号 {order.table_number}, 总额: {order.get_total()}元")


if __name__ == "__main__":
    main()
