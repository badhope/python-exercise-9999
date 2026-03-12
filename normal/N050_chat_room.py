# -----------------------------
# 题目：实现简单的聊天室。
# 描述：支持用户加入、发送消息、查看历史。
# -----------------------------

from datetime import datetime

class Message:
    def __init__(self, message_id, user_id, content):
        self.id = message_id
        self.user_id = user_id
        self.content = content
        self.timestamp = datetime.now()
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content': self.content,
            'timestamp': self.timestamp.isoformat()
        }

class User:
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username
        self.joined_at = datetime.now()
        self.is_online = True
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'joined_at': self.joined_at.isoformat(),
            'is_online': self.is_online
        }

class ChatRoom:
    def __init__(self, room_id, name):
        self.id = room_id
        self.name = name
        self.users = {}
        self.messages = []
        self.next_message_id = 1
    
    def join(self, user):
        self.users[user.id] = user
        system_msg = Message(self.next_message_id, "system", f"{user.username} 加入了聊天室")
        self.messages.append(system_msg)
        self.next_message_id += 1
    
    def leave(self, user_id):
        if user_id in self.users:
            username = self.users[user_id].username
            del self.users[user_id]
            system_msg = Message(self.next_message_id, "system", f"{username} 离开了聊天室")
            self.messages.append(system_msg)
            self.next_message_id += 1
    
    def send_message(self, user_id, content):
        if user_id not in self.users:
            return None
        
        message = Message(self.next_message_id, user_id, content)
        self.messages.append(message)
        self.next_message_id += 1
        return message
    
    def get_messages(self, limit=50):
        return self.messages[-limit:]
    
    def get_online_users(self):
        return [u for u in self.users.values() if u.is_online]
    
    def get_stats(self):
        return {
            'name': self.name,
            'users_count': len(self.users),
            'online_count': len(self.get_online_users()),
            'messages_count': len(self.messages)
        }

class ChatServer:
    def __init__(self):
        self.rooms = {}
        self.users = {}
        self.next_room_id = 1
        self.next_user_id = 1
    
    def create_room(self, name):
        room = ChatRoom(self.next_room_id, name)
        self.rooms[self.next_room_id] = room
        self.next_room_id += 1
        return room.id
    
    def register_user(self, username):
        user = User(self.next_user_id, username)
        self.users[self.next_user_id] = user
        self.next_user_id += 1
        return user
    
    def join_room(self, user_id, room_id):
        user = self.users.get(user_id)
        room = self.rooms.get(room_id)
        if user and room:
            room.join(user)
            return True
        return False
    
    def leave_room(self, user_id, room_id):
        room = self.rooms.get(room_id)
        if room:
            room.leave(user_id)
            return True
        return False
    
    def send_message(self, user_id, room_id, content):
        room = self.rooms.get(room_id)
        if room:
            return room.send_message(user_id, content)
        return None
    
    def get_room_messages(self, room_id, limit=50):
        room = self.rooms.get(room_id)
        if room:
            return room.get_messages(limit)
        return []
    
    def list_rooms(self):
        return [(r.id, r.name, len(r.users)) for r in self.rooms.values()]

def main():
    server = ChatServer()
    
    room_id = server.create_room("Python学习群")
    
    user1 = server.register_user("张三")
    user2 = server.register_user("李四")
    
    server.join_room(user1.id, room_id)
    server.join_room(user2.id, room_id)
    
    server.send_message(user1.id, room_id, "大家好！")
    server.send_message(user2.id, room_id, "你好！")
    
    print("聊天室统计:")
    room = server.rooms[room_id]
    stats = room.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n聊天记录:")
    for msg in room.get_messages():
        sender = msg.user_id if msg.user_id != "system" else "系统"
        print(f"  [{sender}] {msg.content}")


if __name__ == "__main__":
    main()
