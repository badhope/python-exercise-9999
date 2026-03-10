# -----------------------------
# 题目：观察者模式实现消息订阅。
# -----------------------------

class Observer:
    def update(self, message):
        pass

class Subject:
    def __init__(self):
        self.observers = []
        self._state = None
    
    def attach(self, observer):
        self.observers.append(observer)
    
    def detach(self, observer):
        self.observers.remove(observer)
    
    def notify(self):
        for observer in self.observers:
            observer.update(self._state)
    
    @property
    def state(self):
        return self._state
    
    @state.setter
    def state(self, value):
        self._state = value
        self.notify()

class UserObserver(Observer):
    def __init__(self, name):
        self.name = name
    
    def update(self, message):
        print(f"[{self.name}] 收到通知: {message}")

def main():
    subject = Subject()
    user1 = UserObserver("用户A")
    user2 = UserObserver("用户B")
    subject.attach(user1)
    subject.attach(user2)
    subject.state = "系统消息: 版本更新"
    subject.state = "系统消息: 服务器维护"


if __name__ == "__main__":
    main()
