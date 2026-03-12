# -----------------------------
# 题目：学生成绩管理系统。
# 描述：实现学生成绩的录入、查询、统计功能。
# -----------------------------

class Student:
    def __init__(self, student_id, name):
        self.student_id = student_id
        self.name = name
        self.scores = {}
    
    def add_score(self, subject, score):
        self.scores[subject] = score
    
    def get_average(self):
        if not self.scores:
            return 0
        return sum(self.scores.values()) / len(self.scores)
    
    def get_grade(self):
        avg = self.get_average()
        if avg >= 90: return 'A'
        if avg >= 80: return 'B'
        if avg >= 70: return 'C'
        if avg >= 60: return 'D'
        return 'F'

class GradeManager:
    def __init__(self):
        self.students = {}
    
    def add_student(self, student_id, name):
        self.students[student_id] = Student(student_id, name)
    
    def add_score(self, student_id, subject, score):
        if student_id in self.students:
            self.students[student_id].add_score(subject, score)
    
    def get_student(self, student_id):
        return self.students.get(student_id)
    
    def get_class_average(self, subject):
        scores = [s.scores.get(subject, 0) for s in self.students.values() if subject in s.scores]
        return sum(scores) / len(scores) if scores else 0

def main():
    manager = GradeManager()
    manager.add_student("S001", "张三")
    manager.add_score("S001", "数学", 85)
    manager.add_score("S001", "英语", 92)
    student = manager.get_student("S001")
    print(f"{student.name} 平均分: {student.get_average():.1f}, 等级: {student.get_grade()}")


if __name__ == "__main__":
    main()
