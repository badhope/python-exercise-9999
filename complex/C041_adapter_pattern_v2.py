# -----------------------------
# 题目：适配器模式实现第三方API集成。
# -----------------------------

class PaymentProcessor:
    def process_payment(self, amount, currency):
        pass
    
    def refund(self, transaction_id, amount):
        pass

class AlipayProcessor:
    def create_payment(self, total_amount, currency_code):
        return {'status': 'success', 'trade_no': 'ALI123456'}
    
    def close_trade(self, trade_no):
        return {'status': 'closed'}

class WechatProcessor:
    def unifiedorder(self, total_fee, fee_type):
        return {'return_code': 'SUCCESS', 'prepay_id': 'WX123456'}
    
    def refund(self, out_refund_no, refund_fee):
        return {'return_code': 'SUCCESS'}

class StripeProcessor:
    def create_charge(self, amount, currency):
        return {'id': 'ch_123456', 'status': 'succeeded'}
    
    def create_refund(self, charge_id):
        return {'id': 're_123456', 'status': 'succeeded'}

class AlipayAdapter(PaymentProcessor):
    def __init__(self, alipay):
        self.alipay = alipay
    
    def process_payment(self, amount, currency):
        result = self.alipay.create_payment(amount, currency)
        return {'success': result['status'] == 'success', 'transaction_id': result['trade_no']}
    
    def refund(self, transaction_id, amount):
        result = self.alipay.close_trade(transaction_id)
        return {'success': result['status'] == 'closed'}

class WechatAdapter(PaymentProcessor):
    def __init__(self, wechat):
        self.wechat = wechat
    
    def process_payment(self, amount, currency):
        result = self.wechat.unifiedorder(amount, currency)
        return {'success': result['return_code'] == 'SUCCESS', 'transaction_id': result['prepay_id']}
    
    def refund(self, transaction_id, amount):
        result = self.wechat.refund(transaction_id, amount)
        return {'success': result['return_code'] == 'SUCCESS'}

class StripeAdapter(PaymentProcessor):
    def __init__(self, stripe):
        self.stripe = stripe
    
    def process_payment(self, amount, currency):
        result = self.stripe.create_charge(amount, currency)
        return {'success': result['status'] == 'succeeded', 'transaction_id': result['id']}
    
    def refund(self, transaction_id, amount):
        result = self.stripe.create_refund(transaction_id)
        return {'success': result['status'] == 'succeeded'}

class PaymentService:
    def __init__(self):
        self.processors = {}
    
    def register_processor(self, name, processor):
        self.processors[name] = processor
    
    def pay(self, processor_name, amount, currency="CNY"):
        processor = self.processors.get(processor_name)
        if processor:
            return processor.process_payment(amount, currency)
        return {'success': False, 'error': 'Processor not found'}
    
    def refund(self, processor_name, transaction_id, amount):
        processor = self.processors.get(processor_name)
        if processor:
            return processor.refund(transaction_id, amount)
        return {'success': False, 'error': 'Processor not found'}

def main():
    service = PaymentService()
    
    service.register_processor('alipay', AlipayAdapter(AlipayProcessor()))
    service.register_processor('wechat', WechatAdapter(WechatProcessor()))
    service.register_processor('stripe', StripeAdapter(StripeProcessor()))
    
    print("=== 支付测试 ===")
    for name in ['alipay', 'wechat', 'stripe']:
        result = service.pay(name, 100.00, 'CNY')
        print(f"{name}: {result}")
    
    print("\n=== 退款测试 ===")
    for name in ['alipay', 'wechat', 'stripe']:
        result = service.refund(name, 'test_txn_123', 50.00)
        print(f"{name}: {result}")


if __name__ == "__main__":
    main()
