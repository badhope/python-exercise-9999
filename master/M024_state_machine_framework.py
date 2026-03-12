# -----------------------------
# 题目：实现状态机框架。
# -----------------------------

from enum import Enum

class State:
    def __init__(self, name, on_enter=None, on_exit=None):
        self.name = name
        self.on_enter = on_enter
        self.on_exit = on_exit

class Transition:
    def __init__(self, from_state, to_state, event, condition=None):
        self.from_state = from_state
        self.to_state = to_state
        self.event = event
        self.condition = condition

class StateMachine:
    def __init__(self, initial_state):
        self.states = {}
        self.transitions = []
        self.current_state = None
        self.initial_state = initial_state
    
    def add_state(self, state):
        self.states[state.name] = state
    
    def add_transition(self, transition):
        self.transitions.append(transition)
    
    def start(self):
        self.current_state = self.initial_state
        state = self.states.get(self.current_state)
        if state and state.on_enter:
            state.on_enter()
    
    def send_event(self, event, data=None):
        for transition in self.transitions:
            if transition.from_state == self.current_state and transition.event == event:
                if transition.condition and not transition.condition(data):
                    continue
                
                current = self.states.get(self.current_state)
                if current and current.on_exit:
                    current.on_exit()
                
                self.current_state = transition.to_state
                new_state = self.states.get(self.current_state)
                if new_state and new_state.on_enter:
                    new_state.on_enter()
                return True
        return False
    
    def get_state(self):
        return self.current_state

def on_working():
    print("Entering WORKING state")

def on_broken():
    print("Entering BROKEN state")

def on_idle():
    print("Entering IDLE state")

if __name__ == "__main__":
    sm = StateMachine("idle")
    
    sm.add_state(State("idle", on_enter=on_idle))
    sm.add_state(State("working", on_enter=on_working))
    sm.add_state(State("broken", on_enter=on_broken))
    
    sm.add_transition(Transition("idle", "working", "start"))
    sm.add_transition(Transition("working", "idle", "stop"))
    sm.add_transition(Transition("working", "broken", "break"))
    sm.add_transition(Transition("broken", "idle", "repair"))
    
    sm.start()
    print(f"Initial state: {sm.get_state()}")
    
    sm.send_event("start")
    print(f"After start: {sm.get_state()}")
    
    sm.send_event("break")
    print(f"After break: {sm.get_state()}")
    
    sm.send_event("repair")
    print(f"After repair: {sm.get_state()}")
