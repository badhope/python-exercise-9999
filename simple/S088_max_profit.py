# -----------------------------
# 题目：买卖股票最佳时机。
# 描述：计算股票买卖的最大利润。
# -----------------------------

def max_profit(prices):
    if len(prices) < 2:
        return 0
    min_price = prices[0]
    max_profit = 0
    for price in prices[1:]:
        max_profit = max(max_profit, price - min_price)
        min_price = min(min_price, price)
    return max_profit

def main():
    print(f"最大利润: {max_profit([7,1,5,3,6,4])}")


if __name__ == "__main__":
    main()
