# -----------------------------
# 题目：实现简单的投票系统。
# 描述：支持创建投票、投票、统计结果。
# -----------------------------

from datetime import datetime, date

class Poll:
    def __init__(self, poll_id, title, options, end_date=None):
        self.id = poll_id
        self.title = title
        self.options = {option: 0 for option in options}
        self.voters = set()
        self.end_date = end_date
        self.created_at = datetime.now()
        self.is_active = True
    
    def vote(self, option, voter_id):
        if not self.is_active:
            return False, "投票已结束"
        
        if self.end_date and date.today() > self.end_date:
            self.is_active = False
            return False, "投票已过期"
        
        if voter_id in self.voters:
            return False, "已经投过票"
        
        if option not in self.options:
            return False, "无效选项"
        
        self.options[option] += 1
        self.voters.add(voter_id)
        return True, "投票成功"
    
    def get_results(self):
        total = sum(self.options.values())
        results = []
        for option, count in self.options.items():
            percentage = (count / total * 100) if total > 0 else 0
            results.append({
                'option': option,
                'votes': count,
                'percentage': f"{percentage:.1f}%"
            })
        return sorted(results, key=lambda x: x['votes'], reverse=True)
    
    def get_winner(self):
        results = self.get_results()
        if results:
            return results[0]['option']
        return None
    
    def close(self):
        self.is_active = False
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'options': self.options,
            'total_votes': len(self.voters),
            'is_active': self.is_active,
            'end_date': self.end_date.isoformat() if self.end_date else None
        }

class VotingSystem:
    def __init__(self):
        self.polls = {}
        self.next_id = 1
    
    def create_poll(self, title, options, end_date=None):
        if len(options) < 2:
            return None, "至少需要2个选项"
        
        poll = Poll(self.next_id, title, options, end_date)
        self.polls[self.next_id] = poll
        self.next_id += 1
        return poll.id, "创建成功"
    
    def get_poll(self, poll_id):
        return self.polls.get(poll_id)
    
    def vote(self, poll_id, option, voter_id):
        poll = self.polls.get(poll_id)
        if poll:
            return poll.vote(option, voter_id)
        return False, "投票不存在"
    
    def get_results(self, poll_id):
        poll = self.polls.get(poll_id)
        if poll:
            return poll.get_results()
        return []
    
    def get_active_polls(self):
        return [p for p in self.polls.values() if p.is_active]
    
    def close_poll(self, poll_id):
        poll = self.polls.get(poll_id)
        if poll:
            poll.close()
            return True
        return False
    
    def get_stats(self):
        return {
            'total_polls': len(self.polls),
            'active_polls': len(self.get_active_polls()),
            'total_votes': sum(len(p.voters) for p in self.polls.values())
        }

def main():
    system = VotingSystem()
    
    poll_id, _ = system.create_poll(
        "最喜欢的编程语言",
        ["Python", "Java", "JavaScript", "Go"]
    )
    
    system.vote(poll_id, "Python", "user1")
    system.vote(poll_id, "Python", "user2")
    system.vote(poll_id, "Java", "user3")
    system.vote(poll_id, "JavaScript", "user4")
    
    print("投票结果:")
    results = system.get_results(poll_id)
    for result in results:
        print(f"  {result['option']}: {result['votes']}票 ({result['percentage']})")
    
    print(f"\n获胜者: {system.get_poll(poll_id).get_winner()}")


if __name__ == "__main__":
    main()
