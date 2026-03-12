# -----------------------------
# 题目：实现简单的即时通讯系统。
# 描述：管理用户、好友、消息、群组等。
# -----------------------------

from datetime import datetime

class User:
    def __init__(self, user_id, username, password, nickname):
        self.id = user_id
        self.username = username
        self.password = password
        self.nickname = nickname
        self.friends = []
        self.groups = []
        self.status = "offline"
        self.created_at = datetime.now()

class Message:
    def __init__(self, msg_id, sender_id, receiver_id, content, msg_type="private"):
        self.id = msg_id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.content = content
        self.type = msg_type
        self.status = "sent"
        self.created_at = datetime.now()
        self.read_at = None
    
    def mark_read(self):
        self.status = "read"
        self.read_at = datetime.now()

class Group:
    def __init__(self, group_id, name, creator_id):
        self.id = group_id
        self.name = name
        self.creator_id = creator_id
        self.members = [creator_id]
        self.admins = [creator_id]
        self.created_at = datetime.now()
    
    def add_member(self, user_id):
        if user_id not in self.members:
            self.members.append(user_id)
            return True
        return False
    
    def remove_member(self, user_id):
        if user_id in self.members and user_id != self.creator_id:
            self.members.remove(user_id)
            return True
        return False

class IMSystem:
    def __init__(self):
        self.users = {}
        self.messages = []
        self.groups = {}
        self.next_user_id = 1
        self.next_msg_id = 1
        self.next_group_id = 1
    
    def register(self, username, password, nickname):
        for user in self.users.values():
            if user.username == username:
                return None
        
        user = User(self.next_user_id, username, password, nickname)
        self.users[self.next_user_id] = user
        self.next_user_id += 1
        return user.id
    
    def login(self, username, password):
        for user in self.users.values():
            if user.username == username and user.password == password:
                user.status = "online"
                return user.id
        return None
    
    def logout(self, user_id):
        user = self.users.get(user_id)
        if user:
            user.status = "offline"
            return True
        return False
    
    def add_friend(self, user_id, friend_id):
        user = self.users.get(user_id)
        friend = self.users.get(friend_id)
        if user and friend and friend_id not in user.friends:
            user.friends.append(friend_id)
            friend.friends.append(user_id)
            return True
        return False
    
    def send_message(self, sender_id, receiver_id, content, msg_type="private"):
        sender = self.users.get(sender_id)
        if not sender:
            return None
        
        if msg_type == "private":
            receiver = self.users.get(receiver_id)
            if not receiver or receiver_id not in sender.friends:
                return None
        elif msg_type == "group":
            group = self.groups.get(receiver_id)
            if not group or sender_id not in group.members:
                return None
        
        msg = Message(self.next_msg_id, sender_id, receiver_id, content, msg_type)
        self.messages.append(msg)
        self.next_msg_id += 1
        return msg.id
    
    def get_unread_messages(self, user_id):
        unread = []
        for msg in self.messages:
            if msg.receiver_id == user_id and msg.type == "private" and msg.status == "sent":
                unread.append(msg)
            elif msg.type == "group":
                group = self.groups.get(msg.receiver_id)
                if group and user_id in group.members and msg.status == "sent":
                    unread.append(msg)
        return unread
    
    def mark_messages_read(self, user_id, msg_ids):
        for msg in self.messages:
            if msg.id in msg_ids:
                msg.mark_read()
    
    def create_group(self, name, creator_id):
        group = Group(self.next_group_id, name, creator_id)
        self.groups[self.next_group_id] = group
        
        creator = self.users.get(creator_id)
        if creator:
            creator.groups.append(group.id)
        
        self.next_group_id += 1
        return group.id
    
    def join_group(self, user_id, group_id):
        user = self.users.get(user_id)
        group = self.groups.get(group_id)
        if user and group:
            if group.add_member(user_id):
                user.groups.append(group_id)
                return True
        return False
    
    def get_user_friends(self, user_id):
        user = self.users.get(user_id)
        if user:
            return [self.users[fid] for fid in user.friends if fid in self.users]
        return []
    
    def get_user_groups(self, user_id):
        user = self.users.get(user_id)
        if user:
            return [self.groups[gid] for gid in user.groups if gid in self.groups]
        return []
    
    def get_stats(self):
        return {
            'users': len(self.users),
            'online_users': sum(1 for u in self.users.values() if u.status == "online"),
            'messages': len(self.messages),
            'groups': len(self.groups)
        }

def main():
    im = IMSystem()
    
    u1 = im.register("zhangsan", "123456", "张三")
    u2 = im.register("lisi", "123456", "李四")
    u3 = im.register("wangwu", "123456", "王五")
    
    im.login("zhangsan", "123456")
    im.login("lisi", "123456")
    
    im.add_friend(u1, u2)
    im.add_friend(u1, u3)
    
    g1 = im.create_group("技术交流群", u1)
    im.join_group(u2, g1)
    
    im.send_message(u1, u2, "你好！")
    im.send_message(u2, u1, "你好，张三！")
    im.send_message(u1, g1, "大家好！", "group")
    
    print("即时通讯系统统计:")
    stats = im.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print(f"\n用户{u1}的好友:")
    for friend in im.get_user_friends(u1):
        print(f"  {friend.nickname}")


if __name__ == "__main__":
    main()
