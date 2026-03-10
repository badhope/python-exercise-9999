# -----------------------------
# 题目：银行账户类。
# 描述：实现银行账户类，支持存款、取款、查询余额。
# -----------------------------

class BankAccount:
    def __init__(self, account_number, owner, balance=0):
        self.account_number = account_number
        self.owner = owner
        self.balance = balance
    
    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            return True
        return False
    
    def withdraw(self, amount):
        if amount > 0 and self.balance >= amount:
            self.balance -= amount
            return True
        return False
    
    def get_balance(self):
        return self.balance
    
    def __str__(self):
        return f"账户: {self.account_number}, 持有人: {self.owner}, 余额: {self.balance}"

def main():
    account = BankAccount("6222021234567890", "张三", 10000)
    print(account)
    account.deposit(5000)
    print(f"存款后余额: {account.get_balance()}")
    account.withdraw(3000)
    print(f"取款后余额: {account.get_balance()}")


if __name__ == "__main__":
    main()
