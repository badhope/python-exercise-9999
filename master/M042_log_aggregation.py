# -----------------------------
# 题目：实现日志聚合器。
# -----------------------------

import threading
import queue
import time
from collections import defaultdict
from datetime import datetime

class LogEntry:
    def __init__(self, level, message, source=None):
        self.timestamp = datetime.now()
        self.level = level
        self.message = message
        self.source = source or "app"

class LogAggregator:
    def __init__(self, flush_interval=60):
        self.queue = queue.Queue()
        self.buffer = []
        self.flush_interval = flush_interval
        self.running = False
        self.thread = None
        self.handlers = []
    
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._flush_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        self._flush()
    
    def log(self, level, message, source=None):
        entry = LogEntry(level, message, source)
        self.queue.put(entry)
    
    def add_handler(self, handler):
        self.handlers.append(handler)
    
    def _flush_loop(self):
        while self.running:
            time.sleep(self.flush_interval)
            self._flush()
    
    def _flush(self):
        while not self.queue.empty():
            try:
                entry = self.queue.get_nowait()
                self.buffer.append(entry)
            except queue.Empty:
                break
        
        for entry in self.buffer:
            for handler in self.handlers:
                try:
                    handler(entry)
                except Exception as e:
                    print(f"Handler error: {e}")
        
        self.buffer.clear()

def console_handler(entry):
    print(f"[{entry.timestamp}] {entry.level}: {entry.message}")

if __name__ == "__main__":
    aggregator = LogAggregator(flush_interval=1)
    aggregator.add_handler(console_handler)
    aggregator.start()
    
    aggregator.log("INFO", "Application started")
    aggregator.log("ERROR", "Something went wrong")
    aggregator.log("DEBUG", "Processing request")
    
    time.sleep(2)
    aggregator.stop()
