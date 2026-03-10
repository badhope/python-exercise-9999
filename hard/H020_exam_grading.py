# -----------------------------
# 题目：考试评分系统。
# 描述：实现考试评分系统，支持录入成绩、统计平均分、最高分、最低分。
# -----------------------------

class Exam:
    def __init__(self, subject):
        self.subject = subject
        self.scores = []
    
    def add_score(self, score):
        if 0 <= score <= 100:
            self.scores.append(score)
            return True
        return False
    
    def get_average(self):
        if not self.scores:
            return 0
        return sum(self.scores) / len(self.scores)
    
    def get_max(self):
        return max(self.scores) if self.scores else 0
    
    def get_min(self):
        return min(self.scores) if self.scores else 0
    
    def get_pass_count(self):
        return sum(1 for s in self.scores if s >= 60)
    
    def __str__(self):
        return f"科目: {self.subject}, 人数: {len(self.scores)}, 平均分: {self.get_average():.2f}"

def main():
    exam = Exam("Python程序设计")
    for score in [85, 92, 78, 55, 88, 90, 67, 45, 81, 76]:
        exam.add_score(score)
    print(exam)
    print(f"最高分: {exam.get_max()}, 最低分: {exam.get_min()}")
    print(f"及格人数: {exam.get_pass_count()}")


if __name__ == "__main__":
    main()
