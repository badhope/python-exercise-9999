# -----------------------------
# 题目：实现分布式日志系统。
# 描述：支持日志收集、聚合分析、告警通知。
# -----------------------------

import time
import threading
import json
import hashlib
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from queue import Queue
from collections import defaultdict

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

@dataclass
class LogEntry:
    log_id: str
    timestamp: float
    level: LogLevel
    message: str
    source: str
    service: str
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_json(self) -> str:
        return json.dumps({
            'log_id': self.log_id,
            'timestamp': self.timestamp,
            'datetime': datetime.fromtimestamp(self.timestamp).isoformat(),
            'level': self.level.value,
            'message': self.message,
            'source': self.source,
            'service': self.service,
            'trace_id': self.trace_id,
            'span_id': self.span_id,
            'metadata': self.metadata
        })

class LogCollector:
    def __init__(self, batch_size: int = 100, flush_interval: float = 1.0):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self._buffer: List[LogEntry] = []
        self._queue: Queue = Queue()
        self._handlers: List[Callable[[List[LogEntry]], None]] = []
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None
        self._log_counter = 0
        self._lock = threading.Lock()
    
    def add_handler(self, handler: Callable[[List[LogEntry]], None]):
        self._handlers.append(handler)
    
    def collect(self, entry: LogEntry):
        self._queue.put(entry)
    
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
        last_flush = time.time()
        
        while self._running:
            try:
                entry = self._queue.get(timeout=0.1)
                self._buffer.append(entry)
                
                if len(self._buffer) >= self.batch_size:
                    self._flush()
                    last_flush = time.time()
            
            except:
                pass
            
            if time.time() - last_flush >= self.flush_interval and self._buffer:
                self._flush()
    
    def _flush(self):
        if not self._buffer:
            return
        
        batch = self._buffer.copy()
        self._buffer.clear()
        
        for handler in self._handlers:
            try:
                handler(batch)
            except Exception:
                pass

class LogAggregator:
    def __init__(self):
        self._level_counts: Dict[str, Dict[LogLevel, int]] = defaultdict(lambda: defaultdict(int))
        self._error_messages: List[str] = []
        self._service_counts: Dict[str, int] = defaultdict(int)
        self._lock = threading.Lock()
    
    def aggregate(self, entries: List[LogEntry]):
        with self._lock:
            for entry in entries:
                self._level_counts[entry.service][entry.level] += 1
                self._service_counts[entry.service] += 1
                
                if entry.level == LogLevel.ERROR:
                    self._error_messages.append(entry.message)
    
    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            return {
                'level_counts': {
                    service: {level.value: count for level, count in levels.items()}
                    for service, levels in self._level_counts.items()
                },
                'service_counts': dict(self._service_counts),
                'recent_errors': self._error_messages[-10:]
            }

class AlertManager:
    def __init__(self):
        self._rules: Dict[str, Dict[str, Any]] = {}
        self._alert_history: List[Dict[str, Any]] = []
        self._handlers: List[Callable[[Dict[str, Any]], None]] = []
        self._lock = threading.Lock()
    
    def add_rule(
        self,
        rule_id: str,
        level: LogLevel,
        threshold: int,
        window: float,
        handler: Callable = None
    ):
        with self._lock:
            self._rules[rule_id] = {
                'level': level,
                'threshold': threshold,
                'window': window,
                'handler': handler,
                'count': 0,
                'window_start': time.time()
            }
    
    def add_alert_handler(self, handler: Callable[[Dict[str, Any]], None]):
        self._handlers.append(handler)
    
    def check(self, entries: List[LogEntry]):
        with self._lock:
            now = time.time()
            
            for entry in entries:
                for rule_id, rule in self._rules.items():
                    if entry.level == rule['level']:
                        if now - rule['window_start'] > rule['window']:
                            rule['count'] = 0
                            rule['window_start'] = now
                        
                        rule['count'] += 1
                        
                        if rule['count'] >= rule['threshold']:
                            alert = {
                                'rule_id': rule_id,
                                'level': rule['level'].value,
                                'count': rule['count'],
                                'threshold': rule['threshold'],
                                'timestamp': now
                            }
                            
                            self._alert_history.append(alert)
                            
                            for handler in self._handlers:
                                try:
                                    handler(alert)
                                except:
                                    pass
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        with self._lock:
            return self._alert_history.copy()

class DistributedLogSystem:
    def __init__(self):
        self.collector = LogCollector()
        self.aggregator = LogAggregator()
        self.alert_manager = AlertManager()
        self._log_counter = 0
        self._lock = threading.Lock()
    
    def start(self):
        self.collector.add_handler(self.aggregator.aggregate)
        self.collector.add_handler(self.alert_manager.check)
        self.collector.start()
    
    def stop(self):
        self.collector.stop()
    
    def log(
        self,
        level: LogLevel,
        message: str,
        service: str,
        source: str = "app",
        trace_id: str = None,
        metadata: Dict = None
    ):
        with self._lock:
            self._log_counter += 1
            log_id = f"log-{int(time.time())}-{self._log_counter}"
        
        entry = LogEntry(
            log_id=log_id,
            timestamp=time.time(),
            level=level,
            message=message,
            source=source,
            service=service,
            trace_id=trace_id,
            metadata=metadata or {}
        )
        
        self.collector.collect(entry)
    
    def add_alert_rule(
        self,
        rule_id: str,
        level: LogLevel,
        threshold: int,
        window: float
    ):
        self.alert_manager.add_rule(rule_id, level, threshold, window)
    
    def add_alert_handler(self, handler: Callable):
        self.alert_manager.add_alert_handler(handler)
    
    def get_stats(self) -> Dict[str, Any]:
        return self.aggregator.get_stats()

def main():
    log_system = DistributedLogSystem()
    
    def on_alert(alert):
        print(f"[告警] {alert['rule_id']}: {alert['level']} 达到 {alert['count']} 次")
    
    log_system.add_alert_handler(on_alert)
    log_system.add_alert_rule("error-spike", LogLevel.ERROR, 3, 10.0)
    
    log_system.start()
    
    print("发送日志...")
    log_system.log(LogLevel.INFO, "服务启动", "user-service")
    log_system.log(LogLevel.INFO, "用户登录", "user-service", metadata={"user_id": 123})
    log_system.log(LogLevel.WARNING, "内存使用率较高", "monitor-service")
    log_system.log(LogLevel.ERROR, "数据库连接失败", "order-service")
    log_system.log(LogLevel.ERROR, "API请求超时", "order-service")
    log_system.log(LogLevel.ERROR, "缓存服务不可用", "order-service")
    
    time.sleep(2)
    
    print("\n日志统计:")
    stats = log_system.get_stats()
    print(f"服务统计: {stats['service_counts']}")
    print(f"级别分布: {stats['level_counts']}")
    
    print(f"\n告警历史: {len(log_system.alert_manager.get_alerts())} 条")
    
    log_system.stop()

if __name__ == "__main__":
    main()
