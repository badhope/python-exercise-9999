# -----------------------------
# 题目：实现状态机框架。
# 描述：支持状态定义、转换规则、事件触发。
# -----------------------------

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
import time

@dataclass
class Transition:
    from_state: str
    to_state: str
    event: str
    guard: Optional[Callable[[Any], bool]] = None
    action: Optional[Callable[[Any], Any]] = None

@dataclass
class StateConfig:
    name: str
    on_enter: Optional[Callable[[Any], None]] = None
    on_exit: Optional[Callable[[Any], None]] = None
    final: bool = False

class StateMachineError(Exception):
    pass

class StateMachine:
    def __init__(self, name: str, initial_state: str):
        self.name = name
        self.current_state = initial_state
        self.initial_state = initial_state
        self.states: Dict[str, StateConfig] = {}
        self.transitions: List[Transition] = []
        self.history: List[Dict[str, Any]] = []
        self._context: Dict[str, Any] = {}
    
    def add_state(
        self,
        name: str,
        on_enter: Callable = None,
        on_exit: Callable = None,
        final: bool = False
    ):
        self.states[name] = StateConfig(
            name=name,
            on_enter=on_enter,
            on_exit=on_exit,
            final=final
        )
        return self
    
    def add_transition(
        self,
        from_state: str,
        to_state: str,
        event: str,
        guard: Callable = None,
        action: Callable = None
    ):
        self.transitions.append(Transition(
            from_state=from_state,
            to_state=to_state,
            event=event,
            guard=guard,
            action=action
        ))
        return self
    
    def can_transition(self, event: str, context: Any = None) -> bool:
        for t in self.transitions:
            if t.from_state == self.current_state and t.event == event:
                if t.guard is None or t.guard(context):
                    return True
        return False
    
    def trigger(self, event: str, context: Any = None) -> bool:
        if self.is_final():
            raise StateMachineError(f"状态机已处于最终状态: {self.current_state}")
        
        transition = self._find_transition(event, context)
        if not transition:
            return False
        
        old_state = self.current_state
        new_state = transition.to_state
        
        old_config = self.states.get(old_state)
        if old_config and old_config.on_exit:
            old_config.on_exit(context)
        
        if transition.action:
            transition.action(context)
        
        self.current_state = new_state
        
        new_config = self.states.get(new_state)
        if new_config and new_config.on_enter:
            new_config.on_enter(context)
        
        self._record_transition(old_state, new_state, event, context)
        
        return True
    
    def _find_transition(self, event: str, context: Any) -> Optional[Transition]:
        for t in self.transitions:
            if t.from_state == self.current_state and t.event == event:
                if t.guard is None or t.guard(context):
                    return t
        return None
    
    def _record_transition(self, from_state: str, to_state: str, event: str, context: Any):
        self.history.append({
            'from': from_state,
            'to': to_state,
            'event': event,
            'timestamp': time.time(),
            'context': str(context)[:100] if context else None
        })
    
    def is_final(self) -> bool:
        config = self.states.get(self.current_state)
        return config.final if config else False
    
    def get_available_events(self) -> List[str]:
        events = []
        for t in self.transitions:
            if t.from_state == self.current_state:
                events.append(t.event)
        return events
    
    def reset(self):
        self.current_state = self.initial_state
        self.history.clear()
    
    def get_history(self) -> List[Dict[str, Any]]:
        return self.history.copy()
    
    def set_context(self, key: str, value: Any):
        self._context[key] = value
    
    def get_context(self, key: str = None) -> Any:
        if key:
            return self._context.get(key)
        return self._context.copy()

class StateMachineBuilder:
    def __init__(self, name: str):
        self.name = name
        self.initial_state: Optional[str] = None
        self.states: Dict[str, StateConfig] = {}
        self.transitions: List[Transition] = []
    
    def initial(self, state: str) -> 'StateMachineBuilder':
        self.initial_state = state
        return self
    
    def state(
        self,
        name: str,
        on_enter: Callable = None,
        on_exit: Callable = None,
        final: bool = False
    ) -> 'StateMachineBuilder':
        self.states[name] = StateConfig(name, on_enter, on_exit, final)
        return self
    
    def transition(
        self,
        from_state: str,
        to_state: str,
        event: str,
        guard: Callable = None,
        action: Callable = None
    ) -> 'StateMachineBuilder':
        self.transitions.append(Transition(
            from_state, to_state, event, guard, action
        ))
        return self
    
    def build(self) -> StateMachine:
        if not self.initial_state:
            raise StateMachineError("必须设置初始状态")
        
        sm = StateMachine(self.name, self.initial_state)
        
        for name, config in self.states.items():
            sm.add_state(name, config.on_enter, config.on_exit, config.final)
        
        for t in self.transitions:
            sm.add_transition(t.from_state, t.to_state, t.event, t.guard, t.action)
        
        return sm

class OrderStateMachine:
    @staticmethod
    def create() -> StateMachine:
        def on_enter_paid(context):
            print(f"订单 {context.get('order_id')} 已支付")
        
        def on_enter_shipped(context):
            print(f"订单 {context.get('order_id')} 已发货")
        
        def on_enter_completed(context):
            print(f"订单 {context.get('order_id')} 已完成")
        
        def can_cancel(context):
            return context and context.get('cancelable', True)
        
        builder = StateMachineBuilder("order")
        
        return (builder
            .initial("pending")
            .state("pending")
            .state("paid", on_enter=on_enter_paid)
            .state("shipped", on_enter=on_enter_shipped)
            .state("completed", on_enter=on_enter_completed, final=True)
            .state("cancelled", final=True)
            .transition("pending", "paid", "pay")
            .transition("pending", "cancelled", "cancel", guard=can_cancel)
            .transition("paid", "shipped", "ship")
            .transition("paid", "cancelled", "cancel", guard=can_cancel)
            .transition("shipped", "completed", "complete")
            .build())

def main():
    sm = OrderStateMachine.create()
    
    context = {'order_id': 'ORD-001', 'cancelable': True}
    
    print(f"初始状态: {sm.current_state}")
    print(f"可用事件: {sm.get_available_events()}")
    
    sm.trigger('pay', context)
    print(f"支付后状态: {sm.current_state}")
    
    sm.trigger('ship', context)
    print(f"发货后状态: {sm.current_state}")
    
    sm.trigger('complete', context)
    print(f"完成后状态: {sm.current_state}")
    
    print(f"\n是否最终状态: {sm.is_final()}")
    print(f"\n状态历史: {sm.get_history()}")

if __name__ == "__main__":
    main()
