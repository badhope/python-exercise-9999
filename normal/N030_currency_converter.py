# -----------------------------
# 题目：实现简单的汇率换算器。
# 描述：支持多种货币之间的换算。
# -----------------------------

class CurrencyConverter:
    def __init__(self):
        self.rates = {
            'CNY': 1.0,
            'USD': 0.14,
            'EUR': 0.13,
            'GBP': 0.11,
            'JPY': 21.0,
            'KRW': 168.0,
            'HKD': 1.09,
            'TWD': 4.3,
            'SGD': 0.19,
            'AUD': 0.21
        }
        
        self.names = {
            'CNY': '人民币',
            'USD': '美元',
            'EUR': '欧元',
            'GBP': '英镑',
            'JPY': '日元',
            'KRW': '韩元',
            'HKD': '港币',
            'TWD': '新台币',
            'SGD': '新加坡元',
            'AUD': '澳元'
        }
    
    def convert(self, amount, from_currency, to_currency):
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
        if from_currency not in self.rates or to_currency not in self.rates:
            return None
        
        cny_amount = amount / self.rates[from_currency]
        return cny_amount * self.rates[to_currency]
    
    def get_rate(self, from_currency, to_currency):
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
        if from_currency not in self.rates or to_currency not in self.rates:
            return None
        
        return self.rates[to_currency] / self.rates[from_currency]
    
    def list_currencies(self):
        return [(code, name) for code, name in self.names.items()]
    
    def get_cross_rates(self, base_currency='CNY'):
        base_currency = base_currency.upper()
        if base_currency not in self.rates:
            return {}
        
        rates = {}
        for currency in self.rates:
            if currency != base_currency:
                rates[currency] = self.get_rate(base_currency, currency)
        return rates
    
    def format_amount(self, amount, currency):
        currency = currency.upper()
        name = self.names.get(currency, currency)
        return f"{amount:.2f} {currency} ({name})"

def main():
    converter = CurrencyConverter()
    
    print("汇率换算:")
    amount = 100
    print(f"  {amount} CNY = {converter.convert(amount, 'CNY', 'USD'):.2f} USD")
    print(f"  {amount} USD = {converter.convert(amount, 'USD', 'CNY'):.2f} CNY")
    print(f"  {amount} EUR = {converter.convert(amount, 'EUR', 'JPY'):.2f} JPY")
    
    print("\n支持货币:")
    for code, name in converter.list_currencies():
        print(f"  {code}: {name}")


if __name__ == "__main__":
    main()
