# -----------------------------
# 题目：学生成绩管理。
# 描述：创建学生类，管理学生成绩。
# -----------------------------

class Student:
    def __init__(self, name, score):
        self.name = name
        self.score = score
    
    def get_grade(self):
        if self.score >= 90:
            return 'A'
        elif self.score >= 80:
            return 'B'
        elif self.score >= 70:
            return 'C'
        elif self.score >= 60:
            return 'D'
        return 'F'
    
    def __str__(self):
        return f"{self.name}: {self.score} ({self.get_grade()})"

def main():
    students = [
        Student("Alice", 92),
        Student("Bob", 78),
        Student("Charlie", 85)
    ]
    for student in students:
        print(student)


if __name__ == "__main__":
    main()
