# -----------------------------
# 题目：实现简单的日记本。
# 描述：记录和管理日记条目。
# -----------------------------

from datetime import datetime, date

class DiaryEntry:
    def __init__(self, entry_id, title, content, mood="normal"):
        self.id = entry_id
        self.title = title
        self.content = content
        self.mood = mood
        self.date = date.today()
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def update(self, title=None, content=None, mood=None):
        if title:
            self.title = title
        if content:
            self.content = content
        if mood:
            self.mood = mood
        self.updated_at = datetime.now()
    
    def get_word_count(self):
        return len(self.content)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'mood': self.mood,
            'date': self.date.isoformat(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Diary:
    def __init__(self):
        self.entries = {}
        self.next_id = 1
        self.moods = ["happy", "sad", "angry", "normal", "excited"]
    
    def add(self, title, content, mood="normal"):
        entry = DiaryEntry(self.next_id, title, content, mood)
        self.entries[self.next_id] = entry
        self.next_id += 1
        return entry.id
    
    def get(self, entry_id):
        return self.entries.get(entry_id)
    
    def get_by_date(self, target_date):
        return [e for e in self.entries.values() if e.date == target_date]
    
    def get_by_mood(self, mood):
        return [e for e in self.entries.values() if e.mood == mood]
    
    def update(self, entry_id, **kwargs):
        entry = self.entries.get(entry_id)
        if entry:
            entry.update(**kwargs)
            return True
        return False
    
    def delete(self, entry_id):
        if entry_id in self.entries:
            del self.entries[entry_id]
            return True
        return False
    
    def search(self, keyword):
        results = []
        keyword = keyword.lower()
        for entry in self.entries.values():
            if (keyword in entry.title.lower() or 
                keyword in entry.content.lower()):
                results.append(entry)
        return results
    
    def get_date_range(self, start_date, end_date):
        return [
            e for e in self.entries.values()
            if start_date <= e.date <= end_date
        ]
    
    def get_stats(self):
        total = len(self.entries)
        mood_counts = {}
        total_words = 0
        
        for entry in self.entries.values():
            mood_counts[entry.mood] = mood_counts.get(entry.mood, 0) + 1
            total_words += entry.get_word_count()
        
        return {
            'total_entries': total,
            'total_words': total_words,
            'mood_distribution': mood_counts,
            'average_words': total_words // total if total > 0 else 0
        }
    
    def list_entries(self, sort_by='date', reverse=True):
        entries = list(self.entries.values())
        if sort_by == 'date':
            entries.sort(key=lambda e: e.date, reverse=reverse)
        elif sort_by == 'mood':
            entries.sort(key=lambda e: e.mood, reverse=reverse)
        return entries

def main():
    diary = Diary()
    
    diary.add("美好的一天", "今天天气很好，心情愉快", "happy")
    diary.add("工作日志", "完成了项目开发", "normal")
    diary.add("学习笔记", "学习了Python高级特性", "excited")
    
    print("日记统计:")
    stats = diary.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n所有日记:")
    for entry in diary.list_entries():
        print(f"  [{entry.date}] {entry.title} ({entry.mood})")


if __name__ == "__main__":
    main()
