# -----------------------------
# 题目：实现简单的分布式日志系统。
# 描述：支持日志收集、聚合、查询。
# -----------------------------

import time
import threading
import json
from collections import defaultdict
from datetime import datetime

class LogEntry:
    def __init__(self, level, message, source, timestamp=None, **extra):
        self.level = level
        self.message = message
        self.source = source
        self.timestamp = timestamp or time.time()
        self.extra = extra
    
    def to_dict(self):
        return {
            'level': self.level,
            'message': self.message,
            'source': self.source,
            'timestamp': self.timestamp,
            'datetime': datetime.fromtimestamp(self.timestamp).isoformat(),
            **self.extra
        }

class LogCollector:
    def __init__(self, buffer_size=1000):
        self.buffer = []
        self.buffer_size = buffer_size
        self._lock = threading.Lock()
    
    def collect(self, entry):
        with self._lock:
            self.buffer.append(entry)
            if len(self.buffer) >= self.buffer_size:
                self._flush()
    
    def _flush(self):
        logs = self.buffer[:]
        self.buffer.clear()
        return logs

class LogAggregator:
    def __init__(self):
        self.logs_by_level = defaultdict(list)
        self.logs_by_source = defaultdict(list)
        self._lock = threading.Lock()
    
    def aggregate(self, entries):
        with self._lock:
            for entry in entries:
                self.logs_by_level[entry.level].append(entry)
                self.logs_by_source[entry.source].append(entry)
    
    def get_stats(self):
        with self._lock:
            return {
                'by_level': {k: len(v) for k, v in self.logs_by_level.items()},
                'by_source': {k: len(v) for k, v in self.logs_by_source.items()}
            }

class LogQuery:
    def __init__(self, aggregator):
        self.aggregator = aggregator
    
    def query(self, level=None, source=None, start_time=None, end_time=None):
        results = []
        
        if level:
            candidates = self.aggregator.logs_by_level.get(level, [])
        elif source:
            candidates = self.aggregator.logs_by_source.get(source, [])
        else:
            for logs in self.aggregator.logs_by_level.values():
                results.extend(logs)
            candidates = results
            results = []
        
        for entry in candidates:
            if start_time and entry.timestamp < start_time:
                continue
            if end_time and entry.timestamp > end_time:
                continue
            results.append(entry)
        
        return results

class DistributedLogger:
    def __init__(self, source):
        self.source = source
        self.collector = LogCollector()
        self.aggregator = LogAggregator()
        self.query = LogQuery(self.aggregator)
    
    def log(self, level, message, **extra):
        entry = LogEntry(level, message, self.source, **extra)
        self.collector.collect(entry)
        self.aggregator.aggregate([entry])
    
    def info(self, message, **extra):
        self.log('INFO', message, **extra)
    
    def error(self, message, **extra):
        self.log('ERROR', message, **extra)
    
    def warning(self, message, **extra):
        self.log('WARNING', message, **extra)

def main():
    logger = DistributedLogger('order-service')
    
    logger.info("订单创建", order_id=123)
    logger.info("订单处理", order_id=123)
    logger.error("支付失败", order_id=123, error="余额不足")
    logger.warning("库存不足", product_id=456)
    
    print("日志统计:")
    print(json.dumps(logger.query.aggregator.get_stats(), indent=2))
    
    print("\n错误日志:")
    errors = logger.query.query(level='ERROR')
    for entry in errors:
        print(f"  [{entry.level}] {entry.message}")


if __name__ == "__main__":
    main()
