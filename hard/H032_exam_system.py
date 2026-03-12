# -----------------------------
# 题目：实现在线考试系统。
# 描述：管理题库、考试、答题、评分等功能。
# -----------------------------

from datetime import datetime
import random

class Question:
    def __init__(self, question_id, content, options, answer, score, q_type="single"):
        self.id = question_id
        self.content = content
        self.options = options
        self.answer = answer
        self.score = score
        self.type = q_type

class Exam:
    def __init__(self, exam_id, title, duration, total_score):
        self.id = exam_id
        self.title = title
        self.duration = duration
        self.total_score = total_score
        self.questions = []
        self.is_active = True

class Answer:
    def __init__(self, question_id, user_answer):
        self.question_id = question_id
        self.user_answer = user_answer
        self.is_correct = None
        self.score = 0

class ExamRecord:
    def __init__(self, record_id, exam_id, user_id):
        self.id = record_id
        self.exam_id = exam_id
        self.user_id = user_id
        self.answers = {}
        self.start_time = datetime.now()
        self.submit_time = None
        self.total_score = 0
        self.status = "in_progress"

class ExamSystem:
    def __init__(self):
        self.questions = {}
        self.exams = {}
        self.records = {}
        self.next_question_id = 1
        self.next_exam_id = 1
        self.next_record_id = 1
    
    def add_question(self, content, options, answer, score, q_type="single"):
        question = Question(self.next_question_id, content, options, answer, score, q_type)
        self.questions[self.next_question_id] = question
        self.next_question_id += 1
        return question.id
    
    def create_exam(self, title, duration, total_score):
        exam = Exam(self.next_exam_id, title, duration, total_score)
        self.exams[self.next_exam_id] = exam
        self.next_exam_id += 1
        return exam.id
    
    def add_question_to_exam(self, exam_id, question_id):
        exam = self.exams.get(exam_id)
        question = self.questions.get(question_id)
        if exam and question:
            exam.questions.append(question)
            return True
        return False
    
    def start_exam(self, exam_id, user_id):
        exam = self.exams.get(exam_id)
        if not exam or not exam.is_active:
            return None
        
        record = ExamRecord(self.next_record_id, exam_id, user_id)
        self.records[self.next_record_id] = record
        self.next_record_id += 1
        return record.id
    
    def submit_answer(self, record_id, question_id, answer):
        record = self.records.get(record_id)
        if record and record.status == "in_progress":
            ans = Answer(question_id, answer)
            record.answers[question_id] = ans
            return True
        return False
    
    def submit_exam(self, record_id):
        record = self.records.get(record_id)
        exam = self.exams.get(record.exam_id) if record else None
        
        if not record or not exam:
            return None
        
        total = 0
        for question in exam.questions:
            ans = record.answers.get(question.id)
            if ans:
                if ans.user_answer == question.answer:
                    ans.is_correct = True
                    ans.score = question.score
                    total += question.score
                else:
                    ans.is_correct = False
        
        record.total_score = total
        record.submit_time = datetime.now()
        record.status = "completed"
        
        return total
    
    def get_record_detail(self, record_id):
        record = self.records.get(record_id)
        exam = self.exams.get(record.exam_id) if record else None
        
        if not record or not exam:
            return None
        
        details = []
        for question in exam.questions:
            ans = record.answers.get(question.id)
            details.append({
                'question': question.content,
                'user_answer': ans.user_answer if ans else None,
                'correct_answer': question.answer,
                'is_correct': ans.is_correct if ans else None,
                'score': ans.score if ans else 0
            })
        
        return {
            'exam_title': exam.title,
            'total_score': record.total_score,
            'max_score': exam.total_score,
            'details': details
        }
    
    def get_user_records(self, user_id):
        return [r for r in self.records.values() if r.user_id == user_id]
    
    def get_stats(self):
        return {
            'questions': len(self.questions),
            'exams': len(self.exams),
            'records': len(self.records),
            'completed': sum(1 for r in self.records.values() if r.status == "completed")
        }

def main():
    system = ExamSystem()
    
    q1 = system.add_question("Python是什么类型的语言？", 
                            ["编译型", "解释型", "汇编语言", "机器语言"], "B", 10)
    q2 = system.add_question("以下哪个是Python的数据类型？",
                            ["int", "char", "double", "long"], "A", 10)
    q3 = system.add_question("Python使用什么缩进？",
                            ["Tab", "空格", "都可以", "大括号"], "B", 10)
    
    exam_id = system.create_exam("Python基础测试", 60, 30)
    system.add_question_to_exam(exam_id, q1)
    system.add_question_to_exam(exam_id, q2)
    system.add_question_to_exam(exam_id, q3)
    
    record_id = system.start_exam(exam_id, "student001")
    system.submit_answer(record_id, q1, "B")
    system.submit_answer(record_id, q2, "A")
    system.submit_answer(record_id, q3, "A")
    
    score = system.submit_exam(record_id)
    
    print("考试系统统计:")
    stats = system.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print(f"\n考试成绩: {score}分")


if __name__ == "__main__":
    main()
