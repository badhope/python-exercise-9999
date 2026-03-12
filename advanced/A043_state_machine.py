# -----------------------------
# 题目：实现简单的状态机。
# -----------------------------

from typing import Dict, List, Callable, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum

@dataclass
class Transition:
    from_state: str
    to_state: str
    event: str
    condition: Callable = None
    action: Callable = None

@dataclass
class State:
    name: str
    on_enter: Callable = None
    on_exit: Callable = None
    final: bool = False

class StateMachine:
    def __init__(self, initial_state: str):
        self.initial_state = initial_state
        self.current_state = initial_state
        self.states: Dict[str, State] = {}
        self.transitions: List[Transition] = []
        self.history: List[str] = [initial_state]
        self.context: Dict[str, Any] = {}
        self._event_handlers: Dict[str, List[Callable]] = {}
    
    def add_state(self, name: str, on_enter: Callable = None, 
                  on_exit: Callable = None, final: bool = False):
        self.states[name] = State(name, on_enter, on_exit, final)
        return self
    
    def add_transition(self, from_state: str, to_state: str, event: str,
                       condition: Callable = None, action: Callable = None):
        self.transitions.append(Transition(from_state, to_state, event, condition, action))
        return self
    
    def on_event(self, event: str, handler: Callable):
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)
        return self
    
    def can_transition(self, event: str) -> bool:
        for t in self.transitions:
            if t.from_state == self.current_state and t.event == event:
                if t.condition is None or t.condition(self.context):
                    return True
        return False
    
    def trigger(self, event: str) -> bool:
        for t in self.transitions:
            if t.from_state == self.current_state and t.event == event:
                if t.condition is None or t.condition(self.context):
                    self._execute_transition(t)
                    return True
        return False
    
    def _execute_transition(self, transition: Transition):
        from_state = self.states.get(transition.from_state)
        to_state = self.states.get(transition.to_state)
        
        if from_state and from_state.on_exit:
            from_state.on_exit(self.context)
        
        if transition.action:
            transition.action(self.context)
        
        self.current_state = transition.to_state
        self.history.append(transition.to_state)
        
        if to_state and to_state.on_enter:
            to_state.on_enter(self.context)
        
        if transition.event in self._event_handlers:
            for handler in self._event_handlers[transition.event]:
                handler(self.current_state, self.context)
    
    def is_final(self) -> bool:
        state = self.states.get(self.current_state)
        return state.final if state else False
    
    def get_available_events(self) -> List[str]:
        events = []
        for t in self.transitions:
            if t.from_state == self.current_state:
                if t.condition is None or t.condition(self.context):
                    events.append(t.event)
        return events
    
    def reset(self):
        self.current_state = self.initial_state
        self.history = [self.initial_state]
        self.context.clear()

class StateMachineBuilder:
    def __init__(self):
        self._initial: str = None
        self._states: Dict[str, State] = {}
        self._transitions: List[Transition] = []
    
    def initial(self, state: str) -> 'StateMachineBuilder':
        self._initial = state
        return self
    
    def state(self, name: str, on_enter: Callable = None, 
              on_exit: Callable = None, final: bool = False) -> 'StateMachineBuilder':
        self._states[name] = State(name, on_enter, on_exit, final)
        return self
    
    def transition(self, from_state: str, to_state: str, event: str,
                   condition: Callable = None, action: Callable = None) -> 'StateMachineBuilder':
        self._transitions.append(Transition(from_state, to_state, event, condition, action))
        return self
    
    def build(self) -> StateMachine:
        if not self._initial:
            raise ValueError("必须设置初始状态")
        
        sm = StateMachine(self._initial)
        sm.states = self._states.copy()
        sm.transitions = self._transitions.copy()
        return sm

def main():
    print("=== 订单状态机 ===")
    
    def on_enter_processing(context):
        print(f"  进入处理状态，订单ID: {context.get('order_id')}")
    
    def on_exit_processing(context):
        print(f"  离开处理状态")
    
    sm = (StateMachineBuilder()
          .initial("pending")
          .state("pending")
          .state("processing", on_enter=on_enter_processing, on_exit=on_exit_processing)
          .state("shipped")
          .state("delivered", final=True)
          .state("cancelled", final=True)
          .transition("pending", "processing", "process")
          .transition("processing", "shipped", "ship")
          .transition("shipped", "delivered", "deliver")
          .transition("pending", "cancelled", "cancel")
          .transition("processing", "cancelled", "cancel")
          .build())
    
    sm.context['order_id'] = 'ORD-001'
    
    print(f"初始状态: {sm.current_state}")
    print(f"可用事件: {sm.get_available_events()}")
    
    print("\n=== 执行状态转换 ===")
    print(f"处理订单: {sm.trigger('process')}")
    print(f"当前状态: {sm.current_state}")
    
    print(f"\n发货: {sm.trigger('ship')}")
    print(f"当前状态: {sm.current_state}")
    
    print(f"\n送达: {sm.trigger('deliver')}")
    print(f"当前状态: {sm.current_state}")
    print(f"是否终态: {sm.is_final()}")
    
    print(f"\n状态历史: {sm.history}")


if __name__ == "__main__":
    main()
