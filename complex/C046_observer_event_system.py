# -----------------------------
# 题目：观察者模式实现事件系统。
# -----------------------------

class Event:
    def __init__(self, name, data=None):
        self.name = name
        self.data = data or {}
        self.stopped = False
    
    def stop_propagation(self):
        self.stopped = True

class EventListener:
    def handle(self, event):
        pass

class EventEmitter:
    def __init__(self):
        self.listeners = {}
    
    def on(self, event_name, listener):
        if event_name not in self.listeners:
            self.listeners[event_name] = []
        self.listeners[event_name].append(listener)
        return self
    
    def off(self, event_name, listener):
        if event_name in self.listeners:
            if listener in self.listeners[event_name]:
                self.listeners[event_name].remove(listener)
        return self
    
    def emit(self, event_name, data=None):
        event = Event(event_name, data)
        listeners = self.listeners.get(event_name, [])
        
        for listener in listeners:
            if event.stopped:
                break
            listener.handle(event)
        
        return event
    
    def once(self, event_name, listener):
        def wrapper(event):
            self.off(event_name, wrapper)
            listener.handle(event)
        return self.on(event_name, wrapper)

class LogListener(EventListener):
    def __init__(self, prefix=""):
        self.prefix = prefix
    
    def handle(self, event):
        print(f"{self.prefix}[{event.name}] {event.data}")

class EmailListener(EventListener):
    def __init__(self):
        self.sent = []
    
    def handle(self, event):
        email = event.data.get('email')
        if email:
            self.sent.append(email)
            print(f"发送邮件到: {email}")

class CacheListener(EventListener):
    def __init__(self):
        self.cache = {}
    
    def handle(self, event):
        key = event.data.get('cache_key')
        value = event.data.get('cache_value')
        if key and value:
            self.cache[key] = value
            print(f"缓存已更新: {key}")

class EventDispatcher:
    def __init__(self):
        self.emitter = EventEmitter()
    
    def add_listener(self, event_name, listener):
        self.emitter.on(event_name, listener)
    
    def dispatch(self, event_name, data=None):
        return self.emitter.emit(event_name, data)

class ApplicationEvents:
    USER_REGISTERED = 'user.registered'
    USER_LOGIN = 'user.login'
    ORDER_CREATED = 'order.created'
    PAYMENT_SUCCESS = 'payment.success'

def main():
    dispatcher = EventDispatcher()
    
    log_listener = LogListener("[LOG] ")
    email_listener = EmailListener()
    cache_listener = CacheListener()
    
    dispatcher.add_listener(ApplicationEvents.USER_REGISTERED, log_listener)
    dispatcher.add_listener(ApplicationEvents.USER_REGISTERED, email_listener)
    
    dispatcher.add_listener(ApplicationEvents.USER_LOGIN, log_listener)
    dispatcher.add_listener(ApplicationEvents.USER_LOGIN, cache_listener)
    
    dispatcher.add_listener(ApplicationEvents.ORDER_CREATED, log_listener)
    dispatcher.add_listener(ApplicationEvents.PAYMENT_SUCCESS, log_listener)
    
    print("=== 用户注册事件 ===")
    dispatcher.dispatch(ApplicationEvents.USER_REGISTERED, {
        'user_id': 1,
        'username': '张三',
        'email': 'zhangsan@example.com'
    })
    
    print("\n=== 用户登录事件 ===")
    dispatcher.dispatch(ApplicationEvents.USER_LOGIN, {
        'user_id': 1,
        'username': '张三',
        'cache_key': 'user:1:profile',
        'cache_value': {'name': '张三', 'role': 'user'}
    })
    
    print("\n=== 订单创建事件 ===")
    dispatcher.dispatch(ApplicationEvents.ORDER_CREATED, {
        'order_id': 1001,
        'user_id': 1,
        'total': 299.99
    })
    
    print(f"\n已发送邮件数: {len(email_listener.sent)}")
    print(f"缓存条目数: {len(cache_listener.cache)}")


if __name__ == "__main__":
    main()
