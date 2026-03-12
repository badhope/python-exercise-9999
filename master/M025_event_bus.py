# -----------------------------
# 题目：实现事件总线。
# -----------------------------

import threading
from collections import defaultdict

class EventBus:
    def __init__(self):
        self.listeners = defaultdict(list)
        self.lock = threading.Lock()
    
    def subscribe(self, event_type, handler):
        with self.lock:
            self.listeners[event_type].append(handler)
    
    def unsubscribe(self, event_type, handler):
        with self.lock:
            if event_type in self.listeners:
                self.listeners[event_type].remove(handler)
    
    def publish(self, event_type, data=None):
        with self.lock:
            handlers = list(self.listeners.get(event_type, []))
        
        for handler in handlers:
            try:
                handler(data)
            except Exception as e:
                print(f"Handler error: {e}")
    
    def clear(self, event_type=None):
        with self.lock:
            if event_type:
                self.listeners[event_type].clear()
            else:
                self.listeners.clear()

def on_user_registered(data):
    print(f"User registered: {data}")

def on_user_login(data):
    print(f"User logged in: {data}")

if __name__ == "__main__":
    bus = EventBus()
    
    bus.subscribe("user.registered", on_user_registered)
    bus.subscribe("user.login", on_user_login)
    
    bus.publish("user.registered", {"username": "john", "email": "john@example.com"})
    bus.publish("user.login", {"username": "john", "ip": "192.168.1.1"})
    
    bus.unsubscribe("user.registered", on_user_registered)
    bus.publish("user.registered", {"username": "jane"})
