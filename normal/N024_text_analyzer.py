# -----------------------------
# 题目：实现简单的文本统计工具。
# 描述：统计文本的字符数、单词数、句子数等。
# -----------------------------

import re

class TextAnalyzer:
    def __init__(self, text):
        self.text = text
    
    def char_count(self, include_spaces=True):
        if include_spaces:
            return len(self.text)
        return len(self.text.replace(" ", ""))
    
    def word_count(self):
        words = re.findall(r'\b\w+\b', self.text)
        return len(words)
    
    def sentence_count(self):
        sentences = re.split(r'[.!?]+', self.text)
        return len([s for s in sentences if s.strip()])
    
    def paragraph_count(self):
        paragraphs = self.text.split('\n\n')
        return len([p for p in paragraphs if p.strip()])
    
    def line_count(self):
        return len(self.text.split('\n'))
    
    def average_word_length(self):
        words = re.findall(r'\b\w+\b', self.text)
        if not words:
            return 0
        return sum(len(w) for w in words) / len(words)
    
    def average_sentence_length(self):
        sentences = re.split(r'[.!?]+', self.text)
        sentences = [s.strip() for s in sentences if s.strip()]
        if not sentences:
            return 0
        word_counts = [len(re.findall(r'\b\w+\b', s)) for s in sentences]
        return sum(word_counts) / len(word_counts)
    
    def word_frequency(self, top_n=10):
        words = re.findall(r'\b\w+\b', self.text.lower())
        freq = {}
        for word in words:
            freq[word] = freq.get(word, 0) + 1
        sorted_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return sorted_freq[:top_n]
    
    def reading_time(self, wpm=200):
        words = self.word_count()
        minutes = words / wpm
        return f"{int(minutes)}分{int((minutes % 1) * 60)}秒"
    
    def get_report(self):
        return {
            "字符数": self.char_count(),
            "字符数(不含空格)": self.char_count(False),
            "单词数": self.word_count(),
            "句子数": self.sentence_count(),
            "段落数": self.paragraph_count(),
            "行数": self.line_count(),
            "平均词长": f"{self.average_word_length():.2f}",
            "平均句长": f"{self.average_sentence_length():.2f}",
            "预计阅读时间": self.reading_time()
        }

def main():
    text = """
    Python是一种广泛使用的编程语言。它简单易学，功能强大。
    
    Python可以用于Web开发、数据分析、人工智能等领域。
    """
    
    analyzer = TextAnalyzer(text)
    report = analyzer.get_report()
    
    print("文本分析报告:")
    for key, value in report.items():
        print(f"  {key}: {value}")
    
    print("\n高频词汇:")
    for word, count in analyzer.word_frequency(5):
        print(f"  {word}: {count}次")


if __name__ == "__main__":
    main()
