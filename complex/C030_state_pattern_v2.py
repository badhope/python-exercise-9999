# -----------------------------
# 题目：状态模式实现订单状态流转。
# -----------------------------

class OrderState:
    def pay(self, order):
        pass
    
    def ship(self, order):
        pass
    
    def deliver(self, order):
        pass
    
    def cancel(self, order):
        pass
    
    def get_status(self):
        pass

class PendingState(OrderState):
    def pay(self, order):
        order.set_state(PaidState())
        return "订单已支付"
    
    def cancel(self, order):
        order.set_state(CancelledState())
        return "订单已取消"
    
    def get_status(self):
        return "待支付"

class PaidState(OrderState):
    def ship(self, order):
        order.set_state(ShippedState())
        return "订单已发货"
    
    def cancel(self, order):
        order.set_state(CancelledState())
        return "订单已取消，将退款"
    
    def get_status(self):
        return "已支付"

class ShippedState(OrderState):
    def deliver(self, order):
        order.set_state(DeliveredState())
        return "订单已送达"
    
    def get_status(self):
        return "已发货"

class DeliveredState(OrderState):
    def get_status(self):
        return "已送达"

class CancelledState(OrderState):
    def get_status(self):
        return "已取消"

class Order:
    def __init__(self, order_id, items):
        self.order_id = order_id
        self.items = items
        self.state = PendingState()
        self.history = []
    
    def set_state(self, state):
        self.history.append(self.state.get_status())
        self.state = state
    
    def pay(self):
        return self.state.pay(self)
    
    def ship(self):
        return self.state.ship(self)
    
    def deliver(self):
        return self.state.deliver(self)
    
    def cancel(self):
        return self.state.cancel(self)
    
    def get_status(self):
        return self.state.get_status()
    
    def get_history(self):
        return self.history

class OrderSystem:
    def __init__(self):
        self.orders = {}
        self.next_id = 1
    
    def create_order(self, items):
        order = Order(self.next_id, items)
        self.orders[self.next_id] = order
        self.next_id += 1
        return order.order_id
    
    def get_order(self, order_id):
        return self.orders.get(order_id)

def main():
    system = OrderSystem()
    
    order_id = system.create_order(["商品A", "商品B"])
    order = system.get_order(order_id)
    
    print(f"订单ID: {order_id}")
    print(f"初始状态: {order.get_status()}")
    
    print(f"\n支付: {order.pay()}")
    print(f"当前状态: {order.get_status()}")
    
    print(f"\n发货: {order.ship()}")
    print(f"当前状态: {order.get_status()}")
    
    print(f"\n送达: {order.deliver()}")
    print(f"当前状态: {order.get_status()}")
    
    print(f"\n状态历史: {order.get_history()}")
    
    print("\n=== 测试取消流程 ===")
    order2_id = system.create_order(["商品C"])
    order2 = system.get_order(order2_id)
    print(f"取消: {order2.cancel()}")
    print(f"当前状态: {order2.get_status()}")


if __name__ == "__main__":
    main()
