# -----------------------------
# 题目：多态实现支付系统。
# 描述：使用多态实现微信支付、支付宝、银联支付。
# -----------------------------

class PaymentMethod:
    def pay(self, amount):
        raise NotImplementedError

class WeChatPay(PaymentMethod):
    def pay(self, amount):
        return f"微信支付: {amount}元"

class Alipay(PaymentMethod):
    def pay(self, amount):
        return f"支付宝: {amount}元"

class UnionPay(PaymentMethod):
    def pay(self, amount):
        return f"银联支付: {amount}元"

class PaymentProcessor:
    def __init__(self):
        self.payment_methods = {}
    
    def register(self, name, method):
        self.payment_methods[name] = method
    
    def pay(self, method_name, amount):
        if method_name in self.payment_methods:
            return self.payment_methods[method_name].pay(amount)
        return "不支持该支付方式"

def main():
    processor = PaymentProcessor()
    processor.register("wechat", WeChatPay())
    processor.register("alipay", Alipay())
    processor.register("union", UnionPay())
    print(processor.pay("wechat", 99.9))
    print(processor.pay("alipay", 199.9))


if __name__ == "__main__":
    main()
