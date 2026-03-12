# -----------------------------
# 题目：观察者模式实现股票价格监控。
# -----------------------------

class StockObserver:
    def update(self, stock, price):
        pass

class Stock:
    def __init__(self, symbol, name):
        self.symbol = symbol
        self.name = name
        self._price = 0
        self.observers = []
    
    def attach(self, observer):
        self.observers.append(observer)
    
    def detach(self, observer):
        if observer in self.observers:
            self.observers.remove(observer)
    
    def notify(self):
        for observer in self.observers:
            observer.update(self, self._price)
    
    @property
    def price(self):
        return self._price
    
    @price.setter
    def price(self, value):
        old_price = self._price
        self._price = value
        self.notify()
    
    def get_change_percent(self, old_price):
        if old_price == 0:
            return 0
        return ((self._price - old_price) / old_price) * 100

class Investor(StockObserver):
    def __init__(self, name):
        self.name = name
        self.alert_threshold = 5.0
    
    def update(self, stock, price):
        print(f"[{self.name}] {stock.symbol} 价格更新: {price}")

class PriceAlertObserver(StockObserver):
    def __init__(self, threshold=5.0):
        self.threshold = threshold
        self.last_prices = {}
    
    def update(self, stock, price):
        old_price = self.last_prices.get(stock.symbol, price)
        change = stock.get_change_percent(old_price)
        
        if abs(change) >= self.threshold:
            direction = "上涨" if change > 0 else "下跌"
            print(f"[价格预警] {stock.symbol} {direction} {abs(change):.2f}%")
        
        self.last_prices[stock.symbol] = price

class TradingBot(StockObserver):
    def __init__(self, buy_threshold, sell_threshold):
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
        self.last_prices = {}
    
    def update(self, stock, price):
        old_price = self.last_prices.get(stock.symbol, price)
        change = stock.get_change_percent(old_price)
        
        if change >= self.buy_threshold:
            print(f"[交易机器人] 买入信号: {stock.symbol}")
        elif change <= -self.sell_threshold:
            print(f"[交易机器人] 卖出信号: {stock.symbol}")
        
        self.last_prices[stock.symbol] = price

class StockMarket:
    def __init__(self):
        self.stocks = {}
    
    def add_stock(self, symbol, name, price):
        stock = Stock(symbol, name)
        stock.price = price
        self.stocks[symbol] = stock
        return stock
    
    def get_stock(self, symbol):
        return self.stocks.get(symbol)
    
    def update_price(self, symbol, price):
        stock = self.stocks.get(symbol)
        if stock:
            stock.price = price

def main():
    market = StockMarket()
    
    apple = market.add_stock("AAPL", "苹果公司", 150.0)
    google = market.add_stock("GOOGL", "谷歌", 2800.0)
    
    investor1 = Investor("张三")
    investor2 = Investor("李四")
    alert = PriceAlertObserver(3.0)
    bot = TradingBot(2.0, 2.0)
    
    apple.attach(investor1)
    apple.attach(investor2)
    apple.attach(alert)
    apple.attach(bot)
    
    google.attach(investor1)
    google.attach(alert)
    
    print("=== 价格更新 ===")
    market.update_price("AAPL", 155.0)
    print()
    market.update_price("AAPL", 160.0)
    print()
    market.update_price("GOOGL", 2700.0)


if __name__ == "__main__":
    main()
