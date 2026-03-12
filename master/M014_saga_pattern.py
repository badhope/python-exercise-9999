# -----------------------------
# 题目：实现Saga模式。
# 描述：分布式事务编排，支持补偿操作。
# -----------------------------

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass, field
from enum import Enum

class SagaStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    COMPENSATING = "compensating"
    FAILED = "failed"

@dataclass
class SagaStep:
    name: str
    action: Callable[[], bool]
    compensation: Callable[[], bool]
    executed: bool = False
    compensated: bool = False

class Saga:
    def __init__(self, saga_id: str):
        self.saga_id = saga_id
        self.steps: List[SagaStep] = []
        self.status = SagaStatus.PENDING
        self.current_step = 0
        self.results: Dict[str, Any] = {}
    
    def add_step(self, name: str, action: Callable[[], bool], compensation: Callable[[], bool]):
        self.steps.append(SagaStep(name, action, compensation))
        return self
    
    def execute(self) -> bool:
        self.status = SagaStatus.RUNNING
        
        for i, step in enumerate(self.steps):
            self.current_step = i
            try:
                result = step.action()
                if not result:
                    return self._compensate()
                step.executed = True
            except Exception as e:
                self.results[step.name] = str(e)
                return self._compensate()
        
        self.status = SagaStatus.COMPLETED
        return True
    
    def _compensate(self) -> bool:
        self.status = SagaStatus.COMPENSATING
        
        for i in range(self.current_step, -1, -1):
            step = self.steps[i]
            if step.executed and not step.compensated:
                try:
                    step.compensation()
                    step.compensated = True
                except Exception:
                    pass
        
        self.status = SagaStatus.FAILED
        return False

class SagaOrchestrator:
    def __init__(self):
        self.sagas: Dict[str, Saga] = {}
    
    def create_saga(self, saga_id: str) -> Saga:
        saga = Saga(saga_id)
        self.sagas[saga_id] = saga
        return saga
    
    def execute_saga(self, saga_id: str) -> bool:
        saga = self.sagas.get(saga_id)
        if not saga:
            return False
        return saga.execute()
    
    def get_saga_status(self, saga_id: str) -> Optional[SagaStatus]:
        saga = self.sagas.get(saga_id)
        return saga.status if saga else None

class OrderService:
    def __init__(self):
        self.orders: Dict[str, Dict] = {}
    
    def create_order(self, order_id: str, amount: float) -> bool:
        self.orders[order_id] = {'id': order_id, 'amount': amount, 'status': 'created'}
        return True
    
    def cancel_order(self, order_id: str) -> bool:
        if order_id in self.orders:
            self.orders[order_id]['status'] = 'cancelled'
        return True

class PaymentService:
    def __init__(self):
        self.payments: Dict[str, Dict] = {}
        self.should_fail = False
    
    def process_payment(self, order_id: str, amount: float) -> bool:
        if self.should_fail:
            return False
        self.payments[order_id] = {'order_id': order_id, 'amount': amount}
        return True
    
    def refund_payment(self, order_id: str) -> bool:
        if order_id in self.payments:
            del self.payments[order_id]
        return True

class InventoryService:
    def __init__(self):
        self.inventory: Dict[str, int] = {'product-1': 100}
        self.reservations: Dict[str, str] = {}
    
    def reserve_inventory(self, order_id: str, product_id: str, quantity: int) -> bool:
        if self.inventory.get(product_id, 0) >= quantity:
            self.inventory[product_id] -= quantity
            self.reservations[order_id] = product_id
            return True
        return False
    
    def release_inventory(self, order_id: str) -> bool:
        if order_id in self.reservations:
            product_id = self.reservations[order_id]
            self.inventory[product_id] += 1
            del self.reservations[order_id]
        return True

def main():
    order_service = OrderService()
    payment_service = PaymentService()
    inventory_service = InventoryService()
    
    orchestrator = SagaOrchestrator()
    
    saga = orchestrator.create_saga("order-001")
    saga.add_step(
        "create_order",
        lambda: order_service.create_order("order-001", 100.0),
        lambda: order_service.cancel_order("order-001")
    )
    saga.add_step(
        "reserve_inventory",
        lambda: inventory_service.reserve_inventory("order-001", "product-1", 1),
        lambda: inventory_service.release_inventory("order-001")
    )
    saga.add_step(
        "process_payment",
        lambda: payment_service.process_payment("order-001", 100.0),
        lambda: payment_service.refund_payment("order-001")
    )
    
    result = orchestrator.execute_saga("order-001")
    print(f"Saga执行结果: {result}")
    print(f"Saga状态: {orchestrator.get_saga_status('order-001')}")

if __name__ == "__main__":
    main()
