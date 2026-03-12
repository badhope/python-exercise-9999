# -----------------------------
# 题目：健身房会员系统。
# 描述：实现会员卡管理、课程预约、消费记录。
# -----------------------------

class GymMember:
    def __init__(self, member_id, name):
        self.member_id = member_id
        self.name = name
        self.balance = 0
        self.appointments = []
    
    def recharge(self, amount):
        self.balance += amount
    
    def consume(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            return True
        return False

class GymClass:
    def __init__(self, class_id, name, coach, capacity):
        self.class_id = class_id
        self.name = name
        self.coach = coach
        self.capacity = capacity
        self.participants = []

class GymSystem:
    def __init__(self):
        self.members = {}
        self.classes = {}
    
    def register_member(self, member_id, name):
        self.members[member_id] = GymMember(member_id, name)
    
    def add_class(self, class_id, name, coach, capacity):
        self.classes[class_id] = GymClass(class_id, name, coach, capacity)
    
    def book_class(self, member_id, class_id):
        if member_id in self.members and class_id in self.classes:
            gym_class = self.classes[class_id]
            if len(gym_class.participants) < gym_class.capacity:
                gym_class.participants.append(member_id)
                return True
        return False

def main():
    gym = GymSystem()
    gym.register_member("G001", "张三")
    gym.add_class("C001", "瑜伽", "李教练", 20)
    gym.members["G001"].recharge(500)
    gym.book_class("G001", "C001")
    member = gym.members["G001"]
    print(f"{member.name} 余额: {member.balance}元")


if __name__ == "__main__":
    main()
