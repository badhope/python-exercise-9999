# -----------------------------
# 题目：订单管理系统。
# 描述：实现订单的创建、查询、状态管理。
# -----------------------------

class Order:
    def __init__(self, order_id, customer_name):
        self.order_id = order_id
        self.customer_name = customer_name
        self.items = []
        self.status = "待处理"
    
    def add_item(self, name, price, quantity):
        self.items.append({"name": name, "price": price, "quantity": quantity})
    
    def get_total(self):
        return sum(item["price"] * item["quantity"] for item in self.items)
    
    def update_status(self, status):
        self.status = status

class OrderManager:
    def __init__(self):
        self.orders = {}
    
    def create_order(self, order_id, customer_name):
        self.orders[order_id] = Order(order_id, customer_name)
        return self.orders[order_id]
    
    def get_order(self, order_id):
        return self.orders.get(order_id)
    
    def get_orders_by_status(self, status):
        return [o for o in self.orders.values() if o.status == status]

def main():
    manager = OrderManager()
    order = manager.create_order("ORD001", "张三")
    order.add_item("商品A", 100, 2)
    order.add_item("商品B", 50, 1)
    order.update_status("已支付")
    print(f"订单 {order.order_id}: {order.customer_name}, 总额: {order.get_total()}, 状态: {order.status}")


if __name__ == "__main__":
    main()
