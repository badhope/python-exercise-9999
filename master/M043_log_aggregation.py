# -----------------------------
# 题目：实现日志聚合系统。
# 描述：支持日志收集、过滤、聚合分析。
# -----------------------------

import time
import threading
import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from collections import defaultdict
from queue import Queue

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

@dataclass
class LogEntry:
    timestamp: float
    level: LogLevel
    message: str
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp,
            'datetime': datetime.fromtimestamp(self.timestamp).isoformat(),
            'level': self.level.value,
            'message': self.message,
            'source': self.source,
            'metadata': self.metadata
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())

class LogFilter:
    def __init__(self):
        self._level_filter: Optional[LogLevel] = None
        self._source_filter: Optional[str] = None
        self._keyword_filter: Optional[str] = None
        self._time_range: Optional[tuple] = None
    
    def set_level(self, min_level: LogLevel):
        self._level_filter = min_level
        return self
    
    def set_source(self, source: str):
        self._source_filter = source
        return self
    
    def set_keyword(self, keyword: str):
        self._keyword_filter = keyword
        return self
    
    def set_time_range(self, start: float, end: float):
        self._time_range = (start, end)
        return self
    
    def matches(self, entry: LogEntry) -> bool:
        if self._level_filter:
            levels = list(LogLevel)
            if levels.index(entry.level) < levels.index(self._level_filter):
                return False
        
        if self._source_filter and entry.source != self._source_filter:
            return False
        
        if self._keyword_filter and self._keyword_filter not in entry.message:
            return False
        
        if self._time_range:
            start, end = self._time_range
            if not (start <= entry.timestamp <= end):
                return False
        
        return True

class LogAggregator:
    def __init__(self):
        self._counters: Dict[str, int] = defaultdict(int)
        self._level_counts: Dict[LogLevel, int] = defaultdict(int)
        self._source_counts: Dict[str, int] = defaultdict(int)
        self._error_messages: List[str] = []
        self._lock = threading.Lock()
    
    def aggregate(self, entry: LogEntry):
        with self._lock:
            self._counters['total'] += 1
            self._level_counts[entry.level] += 1
            self._source_counts[entry.source] += 1
            
            if entry.level == LogLevel.ERROR:
                self._error_messages.append(entry.message)
    
    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            return {
                'total_logs': self._counters['total'],
                'level_distribution': {
                    level.value: count
                    for level, count in self._level_counts.items()
                },
                'source_distribution': dict(self._source_counts),
                'recent_errors': self._error_messages[-10:]
            }
    
    def reset(self):
        with self._lock:
            self._counters.clear()
            self._level_counts.clear()
            self._source_counts.clear()
            self._error_messages.clear()

class LogCollector:
    def __init__(self, max_logs: int = 10000):
        self.logs: List[LogEntry] = []
        self.max_logs = max_logs
        self._queue: Queue = Queue()
        self._aggregator = LogAggregator()
        self._handlers: List[Callable[[LogEntry], None]] = []
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
    
    def add_handler(self, handler: Callable[[LogEntry], None]):
        self._handlers.append(handler)
    
    def log(
        self,
        level: LogLevel,
        message: str,
        source: str = "app",
        metadata: Dict = None
    ):
        entry = LogEntry(
            timestamp=time.time(),
            level=level,
            message=message,
            source=source,
            metadata=metadata or {}
        )
        
        self._queue.put(entry)
    
    def debug(self, message: str, **kwargs):
        self.log(LogLevel.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        self.log(LogLevel.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self.log(LogLevel.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self.log(LogLevel.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        self.log(LogLevel.CRITICAL, message, **kwargs)
    
    def start(self):
        self._running = True
        self._worker_thread = threading.Thread(target=self._process_loop)
        self._worker_thread.daemon = True
        self._worker_thread.start()
    
    def stop(self):
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=5.0)
    
    def _process_loop(self):
        while self._running:
            try:
                entry = self._queue.get(timeout=1.0)
                self._process_entry(entry)
            except:
                pass
    
    def _process_entry(self, entry: LogEntry):
        with self._lock:
            self.logs.append(entry)
            
            if len(self.logs) > self.max_logs:
                self.logs.pop(0)
        
        self._aggregator.aggregate(entry)
        
        for handler in self._handlers:
            try:
                handler(entry)
            except Exception:
                pass
    
    def query(self, log_filter: LogFilter = None, limit: int = 100) -> List[LogEntry]:
        with self._lock:
            logs = self.logs.copy()
        
        if log_filter:
            logs = [log for log in logs if log_filter.matches(log)]
        
        return logs[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        return self._aggregator.get_stats()

class LogSystem:
    def __init__(self, max_logs: int = 10000):
        self.collector = LogCollector(max_logs)
    
    def start(self):
        self.collector.start()
    
    def stop(self):
        self.collector.stop()
    
    def log(self, level: LogLevel, message: str, **kwargs):
        self.collector.log(level, message, **kwargs)
    
    def query(self, log_filter: LogFilter = None, limit: int = 100) -> List[Dict]:
        entries = self.collector.query(log_filter, limit)
        return [e.to_dict() for e in entries]
    
    def get_stats(self) -> Dict[str, Any]:
        return self.collector.get_stats()

def main():
    log_system = LogSystem(max_logs=1000)
    log_system.start()
    
    log_system.log(LogLevel.INFO, "应用启动", source="main")
    log_system.log(LogLevel.DEBUG, "加载配置", source="config")
    log_system.log(LogLevel.WARNING, "内存使用率较高", source="monitor", metadata={"usage": "85%"})
    log_system.log(LogLevel.ERROR, "数据库连接失败", source="db")
    log_system.log(LogLevel.INFO, "用户登录", source="auth", metadata={"user_id": 123})
    log_system.log(LogLevel.ERROR, "API请求超时", source="api")
    
    time.sleep(0.5)
    
    print("日志统计:")
    stats = log_system.get_stats()
    print(f"  总日志数: {stats['total_logs']}")
    print(f"  级别分布: {stats['level_distribution']}")
    print(f"  来源分布: {stats['source_distribution']}")
    
    print("\n错误日志:")
    error_filter = LogFilter().set_level(LogLevel.ERROR)
    errors = log_system.query(error_filter)
    for err in errors:
        print(f"  [{err['datetime']}] {err['message']}")
    
    log_system.stop()

if __name__ == "__main__":
    main()
