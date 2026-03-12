# -----------------------------
# 题目：实现学生成绩管理系统。
# 描述：管理学生、课程、成绩、统计分析等。
# -----------------------------

from datetime import datetime

class Student:
    def __init__(self, student_id, name, class_name):
        self.id = student_id
        self.name = name
        self.class_name = class_name
        self.scores = {}
    
    def add_score(self, course, score):
        self.scores[course] = score
    
    def get_average(self):
        if not self.scores:
            return 0
        return sum(self.scores.values()) / len(self.scores)
    
    def get_total(self):
        return sum(self.scores.values())
    
    def get_rank_score(self):
        return self.get_total()

class Course:
    def __init__(self, course_id, name, credit):
        self.id = course_id
        self.name = name
        self.credit = credit
        self.scores = {}
    
    def add_score(self, student_id, score):
        self.scores[student_id] = score
    
    def get_average(self):
        if not self.scores:
            return 0
        return sum(self.scores.values()) / len(self.scores)
    
    def get_highest(self):
        if not self.scores:
            return None, 0
        max_id = max(self.scores, key=self.scores.get)
        return max_id, self.scores[max_id]
    
    def get_lowest(self):
        if not self.scores:
            return None, 0
        min_id = min(self.scores, key=self.scores.get)
        return min_id, self.scores[min_id]

class GradeSystem:
    def __init__(self):
        self.students = {}
        self.courses = {}
        self.next_student_id = 1
        self.next_course_id = 1
    
    def add_student(self, name, class_name):
        student = Student(self.next_student_id, name, class_name)
        self.students[self.next_student_id] = student
        self.next_student_id += 1
        return student.id
    
    def add_course(self, name, credit):
        course = Course(self.next_course_id, name, credit)
        self.courses[self.next_course_id] = course
        self.next_course_id += 1
        return course.id
    
    def record_score(self, student_id, course_id, score):
        student = self.students.get(student_id)
        course = self.courses.get(course_id)
        
        if student and course:
            student.add_score(course.name, score)
            course.add_score(student_id, score)
            return True
        return False
    
    def get_student_scores(self, student_id):
        student = self.students.get(student_id)
        if student:
            return {
                'name': student.name,
                'class': student.class_name,
                'scores': student.scores,
                'average': student.get_average(),
                'total': student.get_total()
            }
        return None
    
    def get_course_stats(self, course_id):
        course = self.courses.get(course_id)
        if course:
            highest_id, highest = course.get_highest()
            lowest_id, lowest = course.get_lowest()
            
            return {
                'name': course.name,
                'average': course.get_average(),
                'highest': highest,
                'highest_student': self.students.get(highest_id, Student(0, "", "")).name,
                'lowest': lowest,
                'lowest_student': self.students.get(lowest_id, Student(0, "", "")).name,
                'count': len(course.scores)
            }
        return None
    
    def get_class_ranking(self, class_name):
        students = [s for s in self.students.values() if s.class_name == class_name]
        students.sort(key=lambda s: s.get_rank_score(), reverse=True)
        
        ranking = []
        for i, student in enumerate(students, 1):
            ranking.append({
                'rank': i,
                'name': student.name,
                'total': student.get_total(),
                'average': student.get_average()
            })
        return ranking
    
    def get_grade_distribution(self, course_id):
        course = self.courses.get(course_id)
        if not course:
            return None
        
        distribution = {'优秀': 0, '良好': 0, '及格': 0, '不及格': 0}
        for score in course.scores.values():
            if score >= 90:
                distribution['优秀'] += 1
            elif score >= 80:
                distribution['良好'] += 1
            elif score >= 60:
                distribution['及格'] += 1
            else:
                distribution['不及格'] += 1
        
        return distribution
    
    def get_stats(self):
        return {
            'students': len(self.students),
            'courses': len(self.courses),
            'total_scores': sum(len(s.scores) for s in self.students.values())
        }

def main():
    system = GradeSystem()
    
    s1 = system.add_student("张三", "一班")
    s2 = system.add_student("李四", "一班")
    s3 = system.add_student("王五", "一班")
    
    c1 = system.add_course("数学", 4)
    c2 = system.add_course("英语", 3)
    c3 = system.add_course("物理", 3)
    
    system.record_score(s1, c1, 95)
    system.record_score(s1, c2, 88)
    system.record_score(s1, c3, 92)
    
    system.record_score(s2, c1, 78)
    system.record_score(s2, c2, 85)
    system.record_score(s2, c3, 80)
    
    system.record_score(s3, c1, 65)
    system.record_score(s3, c2, 72)
    system.record_score(s3, c3, 68)
    
    print("成绩系统统计:")
    stats = system.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n一班排名:")
    for item in system.get_class_ranking("一班"):
        print(f"  第{item['rank']}名: {item['name']} - 总分{item['total']}")


if __name__ == "__main__":
    main()
