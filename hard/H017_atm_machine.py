# -----------------------------
# 题目：ATM取款机模拟。
# 描述：实现ATM取款机功能，支持查询余额、取款、存款、转账。
# -----------------------------

class ATM:
    def __init__(self, initial_balance=0):
        self.balance = initial_balance
        self.transaction_history = []
    
    def check_balance(self):
        return self.balance
    
    def withdraw(self, amount):
        if amount > 0 and amount <= self.balance:
            self.balance -= amount
            self.transaction_history.append(f"取款: {amount}")
            return True
        return False
    
    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            self.transaction_history.append(f"存款: {amount}")
            return True
        return False
    
    def transfer(self, amount, target_account):
        if amount > 0 and amount <= self.balance:
            self.balance -= amount
            self.transaction_history.append(f"转账到{target_account}: {amount}")
            return True
        return False
    
    def get_history(self):
        return self.transaction_history

def main():
    atm = ATM(10000)
    print(f"当前余额: {atm.check_balance()}")
    atm.withdraw(2000)
    print(f"取款后余额: {atm.check_balance()}")
    atm.deposit(1000)
    print(f"存款后余额: {atm.check_balance()}")
    atm.transfer(3000, "6222021234567890")
    print(f"转账后余额: {atm.check_balance()}")


if __name__ == "__main__":
    main()
