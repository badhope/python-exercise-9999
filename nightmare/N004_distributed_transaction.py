# -----------------------------
# 题目：实现简单的分布式事务。
# 描述：支持两阶段提交、事务补偿。
# -----------------------------

from enum import Enum
import threading
import time

class TransactionStatus(Enum):
    INIT = "init"
    PREPARING = "preparing"
    PREPARED = "prepared"
    COMMITTING = "committing"
    COMMITTED = "committed"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"

class Participant:
    def __init__(self, name):
        self.name = name
        self.prepared = False
        self.committed = False
    
    def prepare(self):
        print(f"[{self.name}] 准备阶段")
        self.prepared = True
        return True
    
    def commit(self):
        print(f"[{self.name}] 提交阶段")
        self.committed = True
        return True
    
    def rollback(self):
        print(f"[{self.name}] 回滚阶段")
        self.prepared = False
        self.committed = False
        return True

class TransactionCoordinator:
    def __init__(self):
        self.transactions = {}
        self._lock = threading.Lock()
    
    def begin_transaction(self, transaction_id, participants):
        with self._lock:
            self.transactions[transaction_id] = {
                'status': TransactionStatus.INIT,
                'participants': participants,
                'start_time': time.time()
            }
        return transaction_id
    
    def prepare(self, transaction_id):
        with self._lock:
            tx = self.transactions.get(transaction_id)
            if not tx:
                return False
            
            tx['status'] = TransactionStatus.PREPARING
        
        all_prepared = True
        for participant in tx['participants']:
            if not participant.prepare():
                all_prepared = False
                break
        
        with self._lock:
            if all_prepared:
                tx['status'] = TransactionStatus.PREPARED
            else:
                tx['status'] = TransactionStatus.ROLLING_BACK
        
        return all_prepared
    
    def commit(self, transaction_id):
        with self._lock:
            tx = self.transactions.get(transaction_id)
            if not tx or tx['status'] != TransactionStatus.PREPARED:
                return False
            tx['status'] = TransactionStatus.COMMITTING
        
        for participant in tx['participants']:
            participant.commit()
        
        with self._lock:
            tx['status'] = TransactionStatus.COMMITTED
        
        return True
    
    def rollback(self, transaction_id):
        with self._lock:
            tx = self.transactions.get(transaction_id)
            if not tx:
                return False
            tx['status'] = TransactionStatus.ROLLING_BACK
        
        for participant in tx['participants']:
            participant.rollback()
        
        with self._lock:
            tx['status'] = TransactionStatus.ROLLED_BACK
        
        return True
    
    def execute(self, transaction_id, participants):
        self.begin_transaction(transaction_id, participants)
        
        if self.prepare(transaction_id):
            return self.commit(transaction_id)
        else:
            self.rollback(transaction_id)
            return False

def main():
    coordinator = TransactionCoordinator()
    
    db1 = Participant("数据库1")
    db2 = Participant("数据库2")
    db3 = Participant("数据库3")
    
    tx_id = "tx_001"
    success = coordinator.execute(tx_id, [db1, db2, db3])
    
    print(f"\n事务 {'成功' if success else '失败'}")


if __name__ == "__main__":
    main()
