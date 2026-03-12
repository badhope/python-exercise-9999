# -----------------------------
# 题目：实现分布式事务协调器。
# 描述：支持两阶段提交、三阶段提交、Saga模式。
# -----------------------------

import time
import threading
import uuid
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from queue import Queue

class TransactionStatus(Enum):
    INITIALIZED = "initialized"
    PREPARING = "preparing"
    PREPARED = "prepared"
    COMMITTING = "committing"
    COMMITTED = "committed"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"

class ParticipantStatus(Enum):
    READY = "ready"
    PREPARED = "prepared"
    COMMITTED = "committed"
    ABORTED = "aborted"

@dataclass
class Participant:
    participant_id: str
    name: str
    prepare_func: Callable
    commit_func: Callable
    rollback_func: Callable
    status: ParticipantStatus = ParticipantStatus.READY
    timeout: float = 30.0

@dataclass
class Transaction:
    transaction_id: str
    name: str
    participants: List[Participant] = field(default_factory=list)
    status: TransactionStatus = TransactionStatus.INITIALIZED
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    coordinator_log: List[str] = field(default_factory=list)

class TwoPhaseCommitCoordinator:
    def __init__(self):
        self.transactions: Dict[str, Transaction] = {}
        self._lock = threading.Lock()
        self._timeout = 60.0
    
    def begin_transaction(self, name: str) -> str:
        transaction_id = f"tx-{uuid.uuid4().hex[:12]}"
        
        transaction = Transaction(
            transaction_id=transaction_id,
            name=name
        )
        
        with self._lock:
            self.transactions[transaction_id] = transaction
        
        return transaction_id
    
    def add_participant(
        self,
        transaction_id: str,
        participant_id: str,
        name: str,
        prepare_func: Callable,
        commit_func: Callable,
        rollback_func: Callable
    ):
        with self._lock:
            transaction = self.transactions.get(transaction_id)
            if transaction:
                participant = Participant(
                    participant_id=participant_id,
                    name=name,
                    prepare_func=prepare_func,
                    commit_func=commit_func,
                    rollback_func=rollback_func
                )
                transaction.participants.append(participant)
    
    def commit(self, transaction_id: str) -> bool:
        transaction = self.transactions.get(transaction_id)
        if not transaction:
            return False
        
        transaction.status = TransactionStatus.PREPARING
        transaction.started_at = time.time()
        transaction.coordinator_log.append("开始准备阶段")
        
        all_prepared = True
        for participant in transaction.participants:
            try:
                result = participant.prepare_func()
                if result:
                    participant.status = ParticipantStatus.PREPARED
                    transaction.coordinator_log.append(f"{participant.name} 准备成功")
                else:
                    all_prepared = False
                    transaction.coordinator_log.append(f"{participant.name} 准备失败")
                    break
            except Exception as e:
                all_prepared = False
                transaction.coordinator_log.append(f"{participant.name} 准备异常: {str(e)}")
                break
        
        if all_prepared:
            transaction.status = TransactionStatus.COMMITTING
            transaction.coordinator_log.append("所有参与者准备完成，开始提交")
            
            for participant in transaction.participants:
                try:
                    participant.commit_func()
                    participant.status = ParticipantStatus.COMMITTED
                    transaction.coordinator_log.append(f"{participant.name} 提交成功")
                except Exception as e:
                    transaction.coordinator_log.append(f"{participant.name} 提交异常: {str(e)}")
            
            transaction.status = TransactionStatus.COMMITTED
            transaction.completed_at = time.time()
            return True
        else:
            transaction.status = TransactionStatus.ROLLING_BACK
            transaction.coordinator_log.append("准备阶段失败，开始回滚")
            
            for participant in transaction.participants:
                if participant.status == ParticipantStatus.PREPARED:
                    try:
                        participant.rollback_func()
                        participant.status = ParticipantStatus.ABORTED
                        transaction.coordinator_log.append(f"{participant.name} 回滚成功")
                    except Exception as e:
                        transaction.coordinator_log.append(f"{participant.name} 回滚异常: {str(e)}")
            
            transaction.status = TransactionStatus.ROLLED_BACK
            transaction.completed_at = time.time()
            return False
    
    def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        return self.transactions.get(transaction_id)

@dataclass
class SagaStep:
    step_id: str
    name: str
    execute_func: Callable
    compensate_func: Callable
    status: str = "pending"
    result: Any = None
    error: Optional[str] = None

class SagaCoordinator:
    def __init__(self):
        self.sagas: Dict[str, List[SagaStep]] = {}
        self._lock = threading.Lock()
    
    def create_saga(self) -> str:
        saga_id = f"saga-{uuid.uuid4().hex[:12]}"
        with self._lock:
            self.sagas[saga_id] = []
        return saga_id
    
    def add_step(
        self,
        saga_id: str,
        name: str,
        execute_func: Callable,
        compensate_func: Callable
    ):
        with self._lock:
            steps = self.sagas.get(saga_id)
            if steps:
                step = SagaStep(
                    step_id=f"step-{len(steps)}",
                    name=name,
                    execute_func=execute_func,
                    compensate_func=compensate_func
                )
                steps.append(step)
    
    def execute(self, saga_id: str) -> bool:
        steps = self.sagas.get(saga_id)
        if not steps:
            return False
        
        completed_steps = []
        
        for step in steps:
            try:
                step.status = "executing"
                result = step.execute_func()
                step.status = "completed"
                step.result = result
                completed_steps.append(step)
            except Exception as e:
                step.status = "failed"
                step.error = str(e)
                
                for completed_step in reversed(completed_steps):
                    try:
                        completed_step.compensate_func()
                        completed_step.status = "compensated"
                    except Exception:
                        completed_step.status = "compensate_failed"
                
                return False
        
        return True
    
    def get_saga_status(self, saga_id: str) -> Dict[str, Any]:
        steps = self.sagas.get(saga_id)
        if not steps:
            return {}
        
        return {
            'saga_id': saga_id,
            'steps': [
                {
                    'step_id': step.step_id,
                    'name': step.name,
                    'status': step.status
                }
                for step in steps
            ]
        }

def main():
    print("=== 两阶段提交 ===")
    coordinator = TwoPhaseCommitCoordinator()
    
    tx_id = coordinator.begin_transaction("transfer-money")
    
    coordinator.add_participant(
        tx_id, "bank-a", "银行A",
        lambda: True,
        lambda: print("银行A提交"),
        lambda: print("银行A回滚")
    )
    
    coordinator.add_participant(
        tx_id, "bank-b", "银行B",
        lambda: True,
        lambda: print("银行B提交"),
        lambda: print("银行B回滚")
    )
    
    result = coordinator.commit(tx_id)
    tx = coordinator.get_transaction(tx_id)
    print(f"事务结果: {tx.status.value}")
    print(f"协调日志: {tx.coordinator_log}")
    
    print("\n=== Saga模式 ===")
    saga = SagaCoordinator()
    saga_id = saga.create_saga()
    
    saga.add_step(
        saga_id, "创建订单",
        lambda: print("创建订单") or "order-123",
        lambda: print("取消订单")
    )
    
    saga.add_step(
        saga_id, "扣减库存",
        lambda: print("扣减库存"),
        lambda: print("恢复库存")
    )
    
    saga.add_step(
        saga_id, "扣款",
        lambda: print("扣款"),
        lambda: print("退款")
    )
    
    result = saga.execute(saga_id)
    print(f"Saga执行结果: {'成功' if result else '失败'}")
    print(f"Saga状态: {saga.get_saga_status(saga_id)}")

if __name__ == "__main__":
    main()
