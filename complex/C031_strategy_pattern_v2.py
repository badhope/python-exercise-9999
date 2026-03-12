# -----------------------------
# 题目：策略模式实现支付方式选择。
# -----------------------------

class PaymentStrategy:
    def pay(self, amount):
        pass
    
    def get_name(self):
        pass

class AlipayStrategy(PaymentStrategy):
    def __init__(self, account):
        self.account = account
    
    def pay(self, amount):
        return f"支付宝支付 {amount}元，账号: {self.account}"
    
    def get_name(self):
        return "支付宝"

class WechatPayStrategy(PaymentStrategy):
    def __init__(self, openid):
        self.openid = openid
    
    def pay(self, amount):
        return f"微信支付 {amount}元，用户: {self.openid}"
    
    def get_name(self):
        return "微信支付"

class CreditCardStrategy(PaymentStrategy):
    def __init__(self, card_number, cvv):
        self.card_number = card_number
        self.cvv = cvv
    
    def pay(self, amount):
        return f"信用卡支付 {amount}元，卡号: {self.card_number[-4:]}"
    
    def get_name(self):
        return "信用卡"

class BankTransferStrategy(PaymentStrategy):
    def __init__(self, bank_name, account_number):
        self.bank_name = bank_name
        self.account_number = account_number
    
    def pay(self, amount):
        return f"银行转账 {amount}元，{self.bank_name}账户: {self.account_number}"
    
    def get_name(self):
        return "银行转账"

class ShoppingCart:
    def __init__(self):
        self.items = []
    
    def add_item(self, name, price, quantity=1):
        self.items.append({'name': name, 'price': price, 'quantity': quantity})
    
    def get_total(self):
        return sum(item['price'] * item['quantity'] for item in self.items)
    
    def checkout(self, payment_strategy):
        total = self.get_total()
        return payment_strategy.pay(total)

class PaymentFactory:
    _strategies = {}
    
    @classmethod
    def register(cls, name, strategy_class):
        cls._strategies[name] = strategy_class
    
    @classmethod
    def create(cls, name, *args):
        if name in cls._strategies:
            return cls._strategies[name](*args)
        return None

def main():
    PaymentFactory.register('alipay', AlipayStrategy)
    PaymentFactory.register('wechat', WechatPayStrategy)
    PaymentFactory.register('credit', CreditCardStrategy)
    PaymentFactory.register('bank', BankTransferStrategy)
    
    cart = ShoppingCart()
    cart.add_item("商品A", 100)
    cart.add_item("商品B", 200, 2)
    cart.add_item("商品C", 50)
    
    print(f"购物车总价: {cart.get_total()}元\n")
    
    strategies = [
        ('alipay', 'user@example.com'),
        ('wechat', 'wx_123456'),
        ('credit', '6222021234567890', '123'),
        ('bank', '工商银行', '6222021234567890')
    ]
    
    for strategy_info in strategies:
        strategy = PaymentFactory.create(*strategy_info)
        if strategy:
            print(cart.checkout(strategy))


if __name__ == "__main__":
    main()
