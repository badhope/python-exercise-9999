# -----------------------------
# 题目：实现简易事件总线。
# -----------------------------

class EventBus:
    def __init__(self):
        self.listeners = {}
    
    def subscribe(self, event, callback):
        if event not in self.listeners:
            self.listeners[event] = []
        self.listeners[event].append(callback)
    
    def unsubscribe(self, event, callback):
        if event in self.listeners:
            self.listeners[event].remove(callback)
    
    def publish(self, event, *args, **kwargs):
        if event in self.listeners:
            for callback in self.listeners[event]:
                callback(*args, **kwargs)

def on_user_registered(user_id, username):
    print(f"用户注册事件: {username} (ID: {user_id})")

def on_user_login(user_id):
    print(f"用户登录事件: ID {user_id}")

def main():
    bus = EventBus()
    bus.subscribe("user.registered", on_user_registered)
    bus.subscribe("user.login", on_user_login)
    bus.publish("user.registered", 123, "张三")
    bus.publish("user.login", 123)


if __name__ == "__main__":
    main()
