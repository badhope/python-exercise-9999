# -----------------------------
# 题目：中介者模式实现聊天室系统。
# -----------------------------

class User:
    def __init__(self, name, mediator=None):
        self.name = name
        self.mediator = mediator
        self.messages = []
    
    def send(self, message, to=None):
        if self.mediator:
            self.mediator.send_message(self, message, to)
    
    def receive(self, message, from_user):
        self.messages.append((from_user.name, message))
        print(f"[{self.name}] 收到来自 {from_user.name} 的消息: {message}")
    
    def get_messages(self):
        return self.messages

class ChatRoom:
    def __init__(self, name):
        self.name = name
        self.users = {}
    
    def add_user(self, user):
        self.users[user.name] = user
        user.mediator = self
    
    def remove_user(self, user):
        if user.name in self.users:
            del self.users[user.name]
            user.mediator = None
    
    def send_message(self, sender, message, to=None):
        if to:
            if to.name in self.users:
                to.receive(message, sender)
        else:
            for name, user in self.users.items():
                if name != sender.name:
                    user.receive(message, sender)
    
    def get_online_users(self):
        return list(self.users.keys())

class PrivateChat:
    def __init__(self):
        self.user1 = None
        self.user2 = None
    
    def set_users(self, user1, user2):
        self.user1 = user1
        self.user2 = user2
        user1.mediator = self
        user2.mediator = self
    
    def send_message(self, sender, message, to=None):
        receiver = self.user2 if sender == self.user1 else self.user1
        receiver.receive(message, sender)

class ChatServer:
    def __init__(self):
        self.chat_rooms = {}
        self.private_chats = []
    
    def create_room(self, name):
        room = ChatRoom(name)
        self.chat_rooms[name] = room
        return room
    
    def get_room(self, name):
        return self.chat_rooms.get(name)
    
    def create_private_chat(self, user1, user2):
        chat = PrivateChat()
        chat.set_users(user1, user2)
        self.private_chats.append(chat)
        return chat

def main():
    server = ChatServer()
    
    room = server.create_room("技术交流群")
    
    alice = User("Alice")
    bob = User("Bob")
    charlie = User("Charlie")
    
    room.add_user(alice)
    room.add_user(bob)
    room.add_user(charlie)
    
    print("=== 群聊消息 ===")
    alice.send("大家好！")
    bob.send("你好Alice！")
    
    print("\n=== 私聊 ===")
    private = server.create_private_chat(alice, bob)
    alice.send("Bob，有空吗？")
    bob.send("有，什么事？")
    
    print("\n=== 在线用户 ===")
    print(f"技术交流群: {room.get_online_users()}")


if __name__ == "__main__":
    main()
