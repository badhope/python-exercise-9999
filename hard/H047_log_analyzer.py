# -----------------------------
# 题目：实现简单的日志分析系统。
# 描述：收集、解析、分析日志数据。
# -----------------------------

from datetime import datetime
from collections import Counter

class LogEntry:
    def __init__(self, log_id, timestamp, level, source, message):
        self.id = log_id
        self.timestamp = timestamp
        self.level = level
        self.source = source
        self.message = message
    
    def to_dict(self):
        return {
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'level': self.level,
            'source': self.source,
            'message': self.message
        }

class LogAnalyzer:
    def __init__(self):
        self.logs = []
        self.next_id = 1
        self.level_counts = Counter()
        self.source_counts = Counter()
    
    def add_log(self, timestamp, level, source, message):
        entry = LogEntry(self.next_id, timestamp, level, source, message)
        self.logs.append(entry)
        self.level_counts[level] += 1
        self.source_counts[source] += 1
        self.next_id += 1
        return entry.id
    
    def parse_log_line(self, line):
        try:
            parts = line.strip().split(' ', 3)
            if len(parts) >= 4:
                timestamp_str = f"{parts[0]} {parts[1]}"
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                level = parts[2]
                message = parts[3]
                source = "default"
                return self.add_log(timestamp, level, source, message)
        except:
            pass
        return None
    
    def filter_by_level(self, level):
        return [log for log in self.logs if log.level == level]
    
    def filter_by_source(self, source):
        return [log for log in self.logs if log.source == source]
    
    def filter_by_time_range(self, start_time, end_time):
        return [log for log in self.logs 
                if start_time <= log.timestamp <= end_time]
    
    def search(self, keyword):
        keyword = keyword.lower()
        return [log for log in self.logs 
                if keyword in log.message.lower()]
    
    def get_level_distribution(self):
        return dict(self.level_counts)
    
    def get_source_distribution(self):
        return dict(self.source_counts)
    
    def get_error_logs(self):
        return self.filter_by_level("ERROR")
    
    def get_warning_logs(self):
        return self.filter_by_level("WARNING")
    
    def get_recent_logs(self, count=100):
        return self.logs[-count:]
    
    def get_hourly_distribution(self):
        hourly = Counter()
        for log in self.logs:
            hour = log.timestamp.hour
            hourly[hour] += 1
        return dict(sorted(hourly.items()))
    
    def get_statistics(self):
        total = len(self.logs)
        errors = len(self.get_error_logs())
        warnings = len(self.get_warning_logs())
        
        return {
            'total_logs': total,
            'errors': errors,
            'warnings': warnings,
            'error_rate': f"{errors/total*100:.2f}%" if total > 0 else "0%",
            'level_distribution': self.get_level_distribution(),
            'hourly_distribution': self.get_hourly_distribution()
        }
    
    def export_to_dict(self):
        return [log.to_dict() for log in self.logs]
    
    def clear(self):
        self.logs.clear()
        self.level_counts.clear()
        self.source_counts.clear()

def main():
    analyzer = LogAnalyzer()
    
    now = datetime.now()
    
    analyzer.add_log(now, "INFO", "app", "应用启动")
    analyzer.add_log(now, "INFO", "app", "连接数据库成功")
    analyzer.add_log(now, "WARNING", "app", "内存使用率较高")
    analyzer.add_log(now, "ERROR", "app", "数据库连接超时")
    analyzer.add_log(now, "INFO", "app", "用户登录成功")
    analyzer.add_log(now, "ERROR", "api", "API请求失败")
    analyzer.add_log(now, "WARNING", "app", "磁盘空间不足")
    analyzer.add_log(now, "INFO", "app", "任务执行完成")
    
    print("日志分析统计:")
    stats = analyzer.get_statistics()
    print(f"  总日志数: {stats['total_logs']}")
    print(f"  错误数: {stats['errors']}")
    print(f"  警告数: {stats['warnings']}")
    print(f"  错误率: {stats['error_rate']}")
    
    print("\n日志级别分布:")
    for level, count in stats['level_distribution'].items():
        print(f"  {level}: {count}")
    
    print("\n错误日志:")
    for log in analyzer.get_error_logs():
        print(f"  [{log.timestamp}] {log.message}")


if __name__ == "__main__":
    main()
