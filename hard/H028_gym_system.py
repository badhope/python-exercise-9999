# -----------------------------
# 题目：实现健身房会员系统。
# 描述：管理会员、课程、预约等功能。
# -----------------------------

from datetime import datetime, date, timedelta

class Member:
    def __init__(self, member_id, name, phone):
        self.id = member_id
        self.name = name
        self.phone = phone
        self.membership_type = "普通会员"
        self.expire_date = None
        self.balance = 0
        self.join_date = date.today()
    
    def is_active(self):
        if self.expire_date:
            return date.today() <= self.expire_date
        return False
    
    def recharge(self, amount):
        if amount > 0:
            self.balance += amount
            return True
        return False
    
    def consume(self, amount):
        if amount > 0 and self.balance >= amount:
            self.balance -= amount
            return True
        return False

class Course:
    def __init__(self, course_id, name, coach, duration, capacity, price):
        self.id = course_id
        self.name = name
        self.coach = coach
        self.duration = duration
        self.capacity = capacity
        self.price = price

class CourseSchedule:
    def __init__(self, schedule_id, course_id, schedule_date, start_time):
        self.id = schedule_id
        self.course_id = course_id
        self.date = schedule_date
        self.start_time = start_time
        self.participants = []
    
    def is_full(self, capacity):
        return len(self.participants) >= capacity
    
    def add_participant(self, member_id):
        if member_id not in self.participants:
            self.participants.append(member_id)
            return True
        return False
    
    def remove_participant(self, member_id):
        if member_id in self.participants:
            self.participants.remove(member_id)
            return True
        return False

class GymSystem:
    def __init__(self):
        self.members = {}
        self.courses = {}
        self.schedules = {}
        self.next_member_id = 1
        self.next_course_id = 1
        self.next_schedule_id = 1
    
    def add_member(self, name, phone):
        member = Member(self.next_member_id, name, phone)
        self.members[self.next_member_id] = member
        self.next_member_id += 1
        return member.id
    
    def add_course(self, name, coach, duration, capacity, price):
        course = Course(self.next_course_id, name, coach, duration, capacity, price)
        self.courses[self.next_course_id] = course
        self.next_course_id += 1
        return course.id
    
    def add_schedule(self, course_id, schedule_date, start_time):
        schedule = CourseSchedule(self.next_schedule_id, course_id, 
                                 schedule_date, start_time)
        self.schedules[self.next_schedule_id] = schedule
        self.next_schedule_id += 1
        return schedule.id
    
    def renew_membership(self, member_id, months, membership_type="普通会员"):
        member = self.members.get(member_id)
        if not member:
            return False
        
        member.membership_type = membership_type
        if member.expire_date and member.expire_date > date.today():
            member.expire_date += timedelta(days=30 * months)
        else:
            member.expire_date = date.today() + timedelta(days=30 * months)
        return True
    
    def book_course(self, member_id, schedule_id):
        member = self.members.get(member_id)
        schedule = self.schedules.get(schedule_id)
        course = self.courses.get(schedule.course_id) if schedule else None
        
        if not member or not schedule or not course:
            return False, "信息不存在"
        
        if not member.is_active():
            return False, "会员已过期"
        
        if schedule.is_full(course.capacity):
            return False, "课程已满"
        
        if not member.consume(course.price):
            return False, "余额不足"
        
        schedule.add_participant(member_id)
        return True, "预约成功"
    
    def cancel_booking(self, member_id, schedule_id):
        member = self.members.get(member_id)
        schedule = self.schedules.get(schedule_id)
        course = self.courses.get(schedule.course_id) if schedule else None
        
        if not member or not schedule or not course:
            return False, "信息不存在"
        
        if schedule.remove_participant(member_id):
            member.recharge(course.price)
            return True, "取消成功"
        
        return False, "未预约此课程"
    
    def get_member_schedules(self, member_id):
        result = []
        for schedule in self.schedules.values():
            if member_id in schedule.participants:
                course = self.courses.get(schedule.course_id)
                if course:
                    result.append((schedule, course))
        return result
    
    def get_available_schedules(self, schedule_date=None):
        result = []
        for schedule in self.schedules.values():
            if schedule_date is None or schedule.date == schedule_date:
                course = self.courses.get(schedule.course_id)
                if course and not schedule.is_full(course.capacity):
                    result.append((schedule, course))
        return result
    
    def get_stats(self):
        active_members = sum(1 for m in self.members.values() if m.is_active())
        
        return {
            'total_members': len(self.members),
            'active_members': active_members,
            'total_courses': len(self.courses),
            'total_schedules': len(self.schedules)
        }

def main():
    gym = GymSystem()
    
    m1 = gym.add_member("张三", "13800138000")
    m2 = gym.add_member("李四", "13900139000")
    
    gym.renew_membership(m1, 12, "黄金会员")
    gym.renew_membership(m2, 6, "普通会员")
    
    gym.members[m1].recharge(1000)
    gym.members[m2].recharge(500)
    
    c1 = gym.add_course("瑜伽", "王教练", 60, 15, 50)
    c2 = gym.add_course("动感单车", "李教练", 45, 20, 40)
    
    today = date.today()
    s1 = gym.add_schedule(c1, today, "09:00")
    s2 = gym.add_schedule(c2, today, "18:00")
    
    gym.book_course(m1, s1)
    gym.book_course(m2, s1)
    
    print("健身房统计:")
    stats = gym.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print(f"\n会员{m1}预约的课程:")
    for schedule, course in gym.get_member_schedules(m1):
        print(f"  {course.name} - {schedule.date} {schedule.start_time}")


if __name__ == "__main__":
    main()
