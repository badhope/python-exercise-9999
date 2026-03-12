# -----------------------------
# 题目：状态模式实现订单状态。
# 描述：使用状态模式管理订单的不同状态。
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

class PendingState(OrderState):
    def pay(self, order):
        order.state = PaidState()
        return "订单已支付"
    
    def cancel(self, order):
        order.state = CancelledState()
        return "订单已取消"

class PaidState(OrderState):
    def ship(self, order):
        order.state = ShippedState()
        return "订单已发货"

class ShippedState(OrderState):
    def deliver(self, order):
        order.state = DeliveredState()
        return "订单已送达"

class DeliveredState(OrderState):
    pass

class CancelledState(OrderState):
    pass

class Order:
    def __init__(self):
        self.state = PendingState()
    
    def pay(self):
        return self.state.pay(self)
    
    def ship(self):
        return self.state.ship(self)
    
    def deliver(self):
        return self.state.deliver(self)
    
    def cancel(self):
        return self.state.cancel(self)

def main():
    order = Order()
    print(order.pay())
    print(order.ship())
    print(order.deliver())


if __name__ == "__main__":
    main()
