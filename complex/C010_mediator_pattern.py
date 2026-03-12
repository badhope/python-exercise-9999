# -----------------------------
# 题目：中介者模式实现聊天室。
# 描述：使用中介者模式实现用户间的解耦通信。
# -----------------------------

class User:
    def __init__(self, name, mediator):
        self.name = name
        self.mediator = mediator
    
    def send(self, message):
        self.mediator.send(message, self)
    
    def receive(self, message, sender):
        print(f"[{self.name}] 收到来自 {sender.name} 的消息: {message}")

class ChatRoom:
    def __init__(self):
        self.users = []
    
    def add_user(self, user):
        self.users.append(user)
    
    def send(self, message, sender):
        for user in self.users:
            if user != sender:
                user.receive(message, sender)
    
    def broadcast(self, message, sender):
        for user in self.users:
            user.receive(message, sender)

def main():
    chatroom = ChatRoom()
    
    alice = User("Alice", chatroom)
    bob = User("Bob", chatroom)
    charlie = User("Charlie", chatroom)
    
    chatroom.add_user(alice)
    chatroom.add_user(bob)
    chatroom.add_user(charlie)
    
    alice.send("大家好！")


if __name__ == "__main__":
    main()
