# -----------------------------
# 题目：实现银行账户管理系统。
# 描述：管理账户存款、取款、转账等操作。
# -----------------------------

from datetime import datetime

class Transaction:
    def __init__(self, trans_id, trans_type, amount, balance_after, description=""):
        self.id = trans_id
        self.type = trans_type
        self.amount = amount
        self.balance_after = balance_after
        self.description = description
        self.timestamp = datetime.now()

class BankAccount:
    def __init__(self, account_id, owner, password, balance=0):
        self.id = account_id
        self.owner = owner
        self.password = password
        self.balance = balance
        self.transactions = []
        self.is_active = True
        self.next_trans_id = 1
    
    def deposit(self, amount):
        if amount <= 0:
            return False, "存款金额必须大于0"
        
        self.balance += amount
        trans = Transaction(self.next_trans_id, "存款", amount, self.balance)
        self.transactions.append(trans)
        self.next_trans_id += 1
        return True, f"存款成功，当前余额: {self.balance}"
    
    def withdraw(self, amount, password):
        if not self._verify_password(password):
            return False, "密码错误"
        
        if amount <= 0:
            return False, "取款金额必须大于0"
        
        if amount > self.balance:
            return False, "余额不足"
        
        self.balance -= amount
        trans = Transaction(self.next_trans_id, "取款", amount, self.balance)
        self.transactions.append(trans)
        self.next_trans_id += 1
        return True, f"取款成功，当前余额: {self.balance}"
    
    def transfer(self, target_account, amount, password):
        if not self._verify_password(password):
            return False, "密码错误"
        
        if amount <= 0:
            return False, "转账金额必须大于0"
        
        if amount > self.balance:
            return False, "余额不足"
        
        self.balance -= amount
        trans = Transaction(self.next_trans_id, "转出", amount, self.balance, f"转至账户{target_account.id}")
        self.transactions.append(trans)
        self.next_trans_id += 1
        
        target_account.balance += amount
        trans2 = Transaction(target_account.next_trans_id, "转入", amount, target_account.balance, f"来自账户{self.id}")
        target_account.transactions.append(trans2)
        target_account.next_trans_id += 1
        
        return True, f"转账成功，当前余额: {self.balance}"
    
    def _verify_password(self, password):
        return self.password == password
    
    def change_password(self, old_password, new_password):
        if not self._verify_password(old_password):
            return False, "原密码错误"
        
        if len(new_password) < 6:
            return False, "新密码长度至少6位"
        
        self.password = new_password
        return True, "密码修改成功"
    
    def get_transaction_history(self, limit=10):
        return self.transactions[-limit:]
    
    def get_account_info(self):
        return {
            'account_id': self.id,
            'owner': self.owner,
            'balance': self.balance,
            'is_active': self.is_active,
            'transaction_count': len(self.transactions)
        }

class BankSystem:
    def __init__(self):
        self.accounts = {}
        self.next_account_id = 1000
    
    def create_account(self, owner, password, initial_deposit=0):
        if len(password) < 6:
            return None, "密码长度至少6位"
        
        account = BankAccount(self.next_account_id, owner, password, initial_deposit)
        self.accounts[self.next_account_id] = account
        self.next_account_id += 1
        return account.id, "开户成功"
    
    def get_account(self, account_id):
        return self.accounts.get(account_id)
    
    def get_total_deposits(self):
        return sum(acc.balance for acc in self.accounts.values())
    
    def get_stats(self):
        return {
            'total_accounts': len(self.accounts),
            'total_deposits': self.get_total_deposits(),
            'active_accounts': sum(1 for acc in self.accounts.values() if acc.is_active)
        }

def main():
    bank = BankSystem()
    
    acc1, _ = bank.create_account("张三", "123456", 1000)
    acc2, _ = bank.create_account("李四", "654321", 500)
    
    account1 = bank.get_account(acc1)
    account2 = bank.get_account(acc2)
    
    account1.deposit(500)
    account1.withdraw(200, "123456")
    account1.transfer(account2, 300, "123456")
    
    print("银行统计:")
    stats = bank.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print(f"\n账户{acc1}信息:")
    info = account1.get_account_info()
    for key, value in info.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
