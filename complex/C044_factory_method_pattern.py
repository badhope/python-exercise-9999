# -----------------------------
# 题目：工厂方法模式实现日志处理器。
# -----------------------------

from abc import ABC, abstractmethod
from datetime import datetime

class LogHandler(ABC):
    @abstractmethod
    def write(self, level, message):
        pass

class ConsoleLogHandler(LogHandler):
    def write(self, level, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] [{level}] {message}")

class FileLogHandler(LogHandler):
    def __init__(self, filename):
        self.filename = filename
    
    def write(self, level, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.filename, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] [{level}] {message}\n")

class MemoryLogHandler(LogHandler):
    def __init__(self, max_size=100):
        self.logs = []
        self.max_size = max_size
    
    def write(self, level, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.logs.append({'timestamp': timestamp, 'level': level, 'message': message})
        if len(self.logs) > self.max_size:
            self.logs.pop(0)
    
    def get_logs(self):
        return self.logs.copy()

class DatabaseLogHandler(LogHandler):
    def __init__(self):
        self.logs = []
    
    def write(self, level, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.logs.append({'timestamp': timestamp, 'level': level, 'message': message})
    
    def query(self, level=None, start_time=None, end_time=None):
        result = self.logs
        if level:
            result = [log for log in result if log['level'] == level]
        return result

class LogHandlerFactory:
    @staticmethod
    def create_handler(handler_type, **kwargs):
        handlers = {
            'console': ConsoleLogHandler,
            'file': FileLogHandler,
            'memory': MemoryLogHandler,
            'database': DatabaseLogHandler
        }
        
        handler_class = handlers.get(handler_type)
        if handler_class:
            return handler_class(**kwargs)
        raise ValueError(f"Unknown handler type: {handler_type}")

class Logger:
    def __init__(self, name):
        self.name = name
        self.handlers = []
    
    def add_handler(self, handler):
        self.handlers.append(handler)
    
    def log(self, level, message):
        for handler in self.handlers:
            handler.write(level, f"[{self.name}] {message}")
    
    def debug(self, message):
        self.log('DEBUG', message)
    
    def info(self, message):
        self.log('INFO', message)
    
    def warning(self, message):
        self.log('WARNING', message)
    
    def error(self, message):
        self.log('ERROR', message)

class LoggerFactory:
    _loggers = {}
    
    @classmethod
    def get_logger(cls, name):
        if name not in cls._loggers:
            cls._loggers[name] = Logger(name)
        return cls._loggers[name]
    
    @classmethod
    def configure_logger(cls, name, handlers_config):
        logger = cls.get_logger(name)
        for config in handlers_config:
            handler = LogHandlerFactory.create_handler(
                config['type'],
                **config.get('params', {})
            )
            logger.add_handler(handler)
        return logger

def main():
    print("=== 配置日志器 ===")
    LoggerFactory.configure_logger('app', [
        {'type': 'console'},
        {'type': 'memory', 'params': {'max_size': 50}}
    ])
    
    LoggerFactory.configure_logger('api', [
        {'type': 'console'},
        {'type': 'database'}
    ])
    
    print("\n=== 使用日志器 ===")
    app_logger = LoggerFactory.get_logger('app')
    app_logger.info('应用程序启动')
    app_logger.debug('调试信息')
    app_logger.warning('内存使用率较高')
    
    api_logger = LoggerFactory.get_logger('api')
    api_logger.info('API请求: GET /users')
    api_logger.error('数据库连接失败')
    
    print("\n=== 查询日志 ===")
    memory_handler = app_logger.handlers[1]
    print(f"内存日志条数: {len(memory_handler.get_logs())}")


if __name__ == "__main__":
    main()
