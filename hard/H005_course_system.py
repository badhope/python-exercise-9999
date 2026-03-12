# -----------------------------
# 题目：课程管理系统。
# 描述：实现课程的创建、选课、退课功能。
# -----------------------------

class Course:
    def __init__(self, course_id, name, capacity):
        self.course_id = course_id
        self.name = name
        self.capacity = capacity
        self.students = []
    
    def enroll(self, student_id):
        if len(self.students) < self.capacity and student_id not in self.students:
            self.students.append(student_id)
            return True
        return False
    
    def drop(self, student_id):
        if student_id in self.students:
            self.students.remove(student_id)
            return True
        return False
    
    def is_full(self):
        return len(self.students) >= self.capacity

class CourseManager:
    def __init__(self):
        self.courses = {}
    
    def add_course(self, course_id, name, capacity):
        self.courses[course_id] = Course(course_id, name, capacity)
    
    def enroll(self, course_id, student_id):
        if course_id in self.courses:
            return self.courses[course_id].enroll(student_id)
        return False
    
    def get_course(self, course_id):
        return self.courses.get(course_id)

def main():
    manager = CourseManager()
    manager.add_course("CS101", "Python程序设计", 30)
    manager.enroll("CS101", "S001")
    manager.enroll("CS101", "S002")
    course = manager.get_course("CS101")
    print(f"{course.name}: 已选 {len(course.students)}/{course.capacity} 人")


if __name__ == "__main__":
    main()
