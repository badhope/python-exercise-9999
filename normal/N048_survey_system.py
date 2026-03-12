# -----------------------------
# 题目：实现简单的问卷调查系统。
# 描述：创建问卷、收集答案、统计结果。
# -----------------------------

from datetime import datetime

class Question:
    def __init__(self, question_id, text, q_type="single", options=None):
        self.id = question_id
        self.text = text
        self.q_type = q_type
        self.options = options or []
        self.answers = []
    
    def add_answer(self, answer):
        self.answers.append(answer)
    
    def get_statistics(self):
        if self.q_type == "text":
            return {"type": "text", "count": len(self.answers)}
        
        stats = {}
        for answer in self.answers:
            if isinstance(answer, list):
                for a in answer:
                    stats[a] = stats.get(a, 0) + 1
            else:
                stats[answer] = stats.get(answer, 0) + 1
        
        total = len(self.answers)
        result = []
        for option, count in stats.items():
            percentage = (count / total * 100) if total > 0 else 0
            result.append({
                'option': option,
                'count': count,
                'percentage': f"{percentage:.1f}%"
            })
        
        return {
            'type': self.q_type,
            'total': total,
            'results': sorted(result, key=lambda x: x['count'], reverse=True)
        }

class Survey:
    def __init__(self, survey_id, title):
        self.id = survey_id
        self.title = title
        self.questions = []
        self.responses = 0
        self.created_at = datetime.now()
    
    def add_question(self, text, q_type="single", options=None):
        question = Question(len(self.questions) + 1, text, q_type, options)
        self.questions.append(question)
        return question.id
    
    def submit_response(self, answers):
        if len(answers) != len(self.questions):
            return False, "答案数量不匹配"
        
        for i, answer in enumerate(answers):
            self.questions[i].add_answer(answer)
        
        self.responses += 1
        return True, "提交成功"
    
    def get_results(self):
        return {
            'title': self.title,
            'responses': self.responses,
            'questions': [q.get_statistics() for q in self.questions]
        }

class SurveySystem:
    def __init__(self):
        self.surveys = {}
        self.next_id = 1
    
    def create_survey(self, title):
        survey = Survey(self.next_id, title)
        self.surveys[self.next_id] = survey
        self.next_id += 1
        return survey.id
    
    def get_survey(self, survey_id):
        return self.surveys.get(survey_id)
    
    def add_question(self, survey_id, text, q_type="single", options=None):
        survey = self.surveys.get(survey_id)
        if survey:
            return survey.add_question(text, q_type, options)
        return None
    
    def submit_response(self, survey_id, answers):
        survey = self.surveys.get(survey_id)
        if survey:
            return survey.submit_response(answers)
        return False, "问卷不存在"
    
    def get_results(self, survey_id):
        survey = self.surveys.get(survey_id)
        if survey:
            return survey.get_results()
        return None
    
    def list_surveys(self):
        return [(s.id, s.title, s.responses) for s in self.surveys.values()]

def main():
    system = SurveySystem()
    
    survey_id = system.create_survey("用户满意度调查")
    
    system.add_question(survey_id, "您对我们的服务满意吗？", "single", 
                       ["非常满意", "满意", "一般", "不满意"])
    system.add_question(survey_id, "您希望我们改进哪些方面？", "multiple",
                       ["价格", "服务", "质量", "速度"])
    system.add_question(survey_id, "您的建议", "text")
    
    system.submit_response(survey_id, ["满意", ["服务", "质量"], "很好"])
    system.submit_response(survey_id, ["非常满意", ["价格"], "继续努力"])
    system.submit_response(survey_id, ["一般", ["服务", "价格"], "一般般"])
    
    results = system.get_results(survey_id)
    print(f"问卷: {results['title']}")
    print(f"响应数: {results['responses']}")
    
    for i, q in enumerate(results['questions'], 1):
        print(f"\n问题{i}:")
        if q['type'] == 'text':
            print(f"  文本回答数: {q['count']}")
        else:
            for r in q['results']:
                print(f"  {r['option']}: {r['count']} ({r['percentage']})")


if __name__ == "__main__":
    main()
