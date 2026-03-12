# -----------------------------
# 题目：实现简单的日志系统扩展版。
# -----------------------------

import datetime
import threading
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod

class LogLevel(Enum):
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50

@dataclass
class LogRecord:
    level: LogLevel
    message: str
    logger_name: str
    timestamp: datetime.datetime
    extra: Dict[str, Any] = None
    exception: Exception = None

class Handler(ABC):
    def __init__(self, level: LogLevel = LogLevel.DEBUG):
        self.level = level
        self.formatter: 'Formatter' = None
    
    def set_formatter(self, formatter: 'Formatter'):
        self.formatter = formatter
    
    def handle(self, record: LogRecord):
        if record.level.value >= self.level.value:
            self.emit(record)
    
    @abstractmethod
    def emit(self, record: LogRecord):
        pass

class Formatter:
    def __init__(self, fmt: str = None):
        self.fmt = fmt or "[{timestamp}] [{level}] {name}: {message}"
    
    def format(self, record: LogRecord) -> str:
        return self.fmt.format(
            timestamp=record.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            level=record.level.name,
            name=record.logger_name,
            message=record.message
        )

class ConsoleHandler(Handler):
    def emit(self, record: LogRecord):
        message = self.formatter.format(record) if self.formatter else record.message
        print(message)

class FileHandler(Handler):
    def __init__(self, filename: str, level: LogLevel = LogLevel.DEBUG):
        super().__init__(level)
        self.filename = filename
        self._lock = threading.Lock()
    
    def emit(self, record: LogRecord):
        message = self.formatter.format(record) if self.formatter else record.message
        with self._lock:
            with open(self.filename, 'a', encoding='utf-8') as f:
                f.write(message + '\n')

class MemoryHandler(Handler):
    def __init__(self, max_size: int = 1000, level: LogLevel = LogLevel.DEBUG):
        super().__init__(level)
        self.max_size = max_size
        self.records: List[LogRecord] = []
        self._lock = threading.Lock()
    
    def emit(self, record: LogRecord):
        with self._lock:
            self.records.append(record)
            if len(self.records) > self.max_size:
                self.records.pop(0)
    
    def get_records(self, level: LogLevel = None) -> List[LogRecord]:
        with self._lock:
            if level:
                return [r for r in self.records if r.level.value >= level.value]
            return self.records.copy()

class Filter:
    def __init__(self, predicate: Callable[[LogRecord], bool]):
        self.predicate = predicate
    
    def filter(self, record: LogRecord) -> bool:
        return self.predicate(record)

class Logger:
    def __init__(self, name: str, level: LogLevel = LogLevel.INFO):
        self.name = name
        self.level = level
        self.handlers: List[Handler] = []
        self.filters: List[Filter] = []
        self.parent: Optional[Logger] = None
        self.children: Dict[str, Logger] = {}
    
    def add_handler(self, handler: Handler):
        self.handlers.append(handler)
    
    def add_filter(self, filter: Filter):
        self.filters.append(filter)
    
    def _log(self, level: LogLevel, message: str, **kwargs):
        if level.value < self.level.value:
            return
        
        record = LogRecord(
            level=level,
            message=message,
            logger_name=self.name,
            timestamp=datetime.datetime.now(),
            extra=kwargs
        )
        
        for f in self.filters:
            if not f.filter(record):
                return
        
        for handler in self.handlers:
            handler.handle(record)
        
        if self.parent:
            self.parent._log(level, message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        self._log(LogLevel.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        self._log(LogLevel.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log(LogLevel.WARNING, message, **kwargs)
    
    def error(self, message: str, exception: Exception = None, **kwargs):
        self._log(LogLevel.ERROR, message, exception=exception, **kwargs)
    
    def critical(self, message: str, **kwargs):
        self._log(LogLevel.CRITICAL, message, **kwargs)

class LoggerManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._loggers: Dict[str, Logger] = {}
                    cls._instance.root = Logger('root')
        return cls._instance
    
    def get_logger(self, name: str) -> Logger:
        if name in self._loggers:
            return self._loggers[name]
        
        logger = Logger(name)
        
        parts = name.split('.')
        if len(parts) > 1:
            parent_name = '.'.join(parts[:-1])
            parent = self.get_logger(parent_name)
            logger.parent = parent
            parent.children[parts[-1]] = logger
        else:
            logger.parent = self.root
        
        self._loggers[name] = logger
        return logger
    
    def configure_root(self, handlers: List[Handler], level: LogLevel = LogLevel.INFO):
        self.root.handlers = handlers
        self.root.level = level

def main():
    manager = LoggerManager()
    
    console_handler = ConsoleHandler()
    console_handler.set_formatter(Formatter("[{timestamp}] [{level}] {name}: {message}"))
    
    memory_handler = MemoryHandler(max_size=100)
    
    manager.configure_root([console_handler, memory_handler], LogLevel.DEBUG)
    
    logger = manager.get_logger('app.service')
    
    print("=== 日志输出 ===")
    logger.debug("调试信息")
    logger.info("应用启动")
    logger.warning("内存使用率较高")
    logger.error("数据库连接失败")
    logger.critical("系统崩溃")
    
    print(f"\n内存日志记录数: {len(memory_handler.get_records())}")
    
    print("\n=== 带过滤器的日志 ===")
    filtered_logger = manager.get_logger('app.filtered')
    filtered_logger.add_filter(Filter(lambda r: 'secret' not in r.message))
    
    filtered_logger.info("普通消息")
    filtered_logger.info("secret消息")


if __name__ == "__main__":
    main()
