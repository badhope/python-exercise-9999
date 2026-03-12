# -----------------------------
# 题目：实现简单的问答系统。
# 描述：管理问题、回答、投票、采纳等。
# -----------------------------

from datetime import datetime

class User:
    def __init__(self, user_id, username, email):
        self.id = user_id
        self.username = username
        self.email = email
        self.reputation = 0
        self.questions = []
        self.answers = []
        self.created_at = datetime.now()

class Question:
    def __init__(self, question_id, author_id, title, content, tags):
        self.id = question_id
        self.author_id = author_id
        self.title = title
        self.content = content
        self.tags = tags
        self.answers = []
        self.votes = 0
        self.views = 0
        self.accepted_answer_id = None
        self.status = "open"
        self.created_at = datetime.now()
    
    def is_answered(self):
        return self.accepted_answer_id is not None

class Answer:
    def __init__(self, answer_id, question_id, author_id, content):
        self.id = answer_id
        self.question_id = question_id
        self.author_id = author_id
        self.content = content
        self.votes = 0
        self.is_accepted = False
        self.created_at = datetime.now()

class QASystem:
    def __init__(self):
        self.users = {}
        self.questions = {}
        self.answers = {}
        self.next_user_id = 1
        self.next_question_id = 1
        self.next_answer_id = 1
    
    def register(self, username, email):
        user = User(self.next_user_id, username, email)
        self.users[self.next_user_id] = user
        self.next_user_id += 1
        return user.id
    
    def ask_question(self, author_id, title, content, tags):
        user = self.users.get(author_id)
        if user:
            question = Question(self.next_question_id, author_id, title, content, tags)
            self.questions[self.next_question_id] = question
            user.questions.append(question.id)
            self.next_question_id += 1
            return question.id
        return None
    
    def answer_question(self, question_id, author_id, content):
        question = self.questions.get(question_id)
        user = self.users.get(author_id)
        if question and user:
            answer = Answer(self.next_answer_id, question_id, author_id, content)
            self.answers[self.next_answer_id] = answer
            question.answers.append(answer.id)
            user.answers.append(answer.id)
            self.next_answer_id += 1
            return answer.id
        return None
    
    def vote_question(self, question_id, vote_type):
        question = self.questions.get(question_id)
        if question:
            if vote_type == "up":
                question.votes += 1
                author = self.users.get(question.author_id)
                if author:
                    author.reputation += 5
            elif vote_type == "down":
                question.votes -= 1
                author = self.users.get(question.author_id)
                if author:
                    author.reputation -= 2
            return True
        return False
    
    def vote_answer(self, answer_id, vote_type):
        answer = self.answers.get(answer_id)
        if answer:
            if vote_type == "up":
                answer.votes += 1
                author = self.users.get(answer.author_id)
                if author:
                    author.reputation += 10
            elif vote_type == "down":
                answer.votes -= 1
                author = self.users.get(answer.author_id)
                if author:
                    author.reputation -= 2
            return True
        return False
    
    def accept_answer(self, question_id, answer_id, user_id):
        question = self.questions.get(question_id)
        answer = self.answers.get(answer_id)
        
        if question and answer and question.author_id == user_id:
            if question.accepted_answer_id is None:
                question.accepted_answer_id = answer_id
                answer.is_accepted = True
                question.status = "solved"
                
                author = self.users.get(answer.author_id)
                if author:
                    author.reputation += 15
                return True
        return False
    
    def view_question(self, question_id):
        question = self.questions.get(question_id)
        if question:
            question.views += 1
            return {
                'title': question.title,
                'content': question.content,
                'tags': question.tags,
                'votes': question.votes,
                'views': question.views,
                'answer_count': len(question.answers),
                'is_answered': question.is_answered()
            }
        return None
    
    def get_question_answers(self, question_id):
        question = self.questions.get(question_id)
        if question:
            answers = [self.answers[aid] for aid in question.answers if aid in self.answers]
            answers.sort(key=lambda x: (x.is_accepted, x.votes), reverse=True)
            return answers
        return []
    
    def search_questions(self, keyword):
        keyword = keyword.lower()
        return [q for q in self.questions.values() 
                if keyword in q.title.lower() or keyword in q.content.lower()]
    
    def get_questions_by_tag(self, tag):
        return [q for q in self.questions.values() if tag in q.tags]
    
    def get_hot_questions(self, limit=10):
        questions = list(self.questions.values())
        questions.sort(key=lambda x: x.votes + len(x.answers) * 3, reverse=True)
        return questions[:limit]
    
    def get_unanswered_questions(self):
        return [q for q in self.questions.values() if not q.answers]
    
    def get_stats(self):
        return {
            'users': len(self.users),
            'questions': len(self.questions),
            'answers': len(self.answers),
            'solved': sum(1 for q in self.questions.values() if q.is_answered())
        }

def main():
    qa = QASystem()
    
    u1 = qa.register("张三", "zhangsan@example.com")
    u2 = qa.register("李四", "lisi@example.com")
    u3 = qa.register("王五", "wangwu@example.com")
    
    q1 = qa.ask_question(u1, "Python如何读取文件？", "请问Python中如何读取文件？", ["Python", "文件操作"])
    q2 = qa.ask_question(u2, "什么是装饰器？", "请解释Python装饰器的概念", ["Python", "装饰器"])
    
    a1 = qa.answer_question(q1, u2, "可以使用open()函数...")
    a2 = qa.answer_question(q1, u3, "推荐使用with语句...")
    
    qa.vote_question(q1, "up")
    qa.vote_answer(a1, "up")
    qa.accept_answer(q1, a1, u1)
    
    print("问答系统统计:")
    stats = qa.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print(f"\n热门问题:")
    for q in qa.get_hot_questions():
        print(f"  {q.title} - {q.votes}票, {len(q.answers)}回答")


if __name__ == "__main__":
    main()
