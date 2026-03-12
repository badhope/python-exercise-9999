# -----------------------------
# 题目：会员管理系统。
# 描述：实现会员注册、积分管理、等级升级。
# -----------------------------

class Member:
    def __init__(self, member_id, name):
        self.member_id = member_id
        self.name = name
        self.points = 0
    
    def add_points(self, points):
        self.points += points
    
    def use_points(self, points):
        if self.points >= points:
            self.points -= points
            return True
        return False
    
    def get_level(self):
        if self.points >= 10000:
            return "钻石会员"
        elif self.points >= 5000:
            return "黄金会员"
        elif self.points >= 1000:
            return "白银会员"
        return "普通会员"

class MemberManager:
    def __init__(self):
        self.members = {}
    
    def register(self, member_id, name):
        self.members[member_id] = Member(member_id, name)
    
    def get_member(self, member_id):
        return self.members.get(member_id)
    
    def get_members_by_level(self, level):
        return [m for m in self.members.values() if m.get_level() == level]

def main():
    manager = MemberManager()
    manager.register("M001", "张三")
    member = manager.get_member("M001")
    member.add_points(1500)
    print(f"{member.name}: 积分 {member.points}, 等级: {member.get_level()}")


if __name__ == "__main__":
    main()
