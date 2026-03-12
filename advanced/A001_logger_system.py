# -----------------------------
# 题目：实现简单的日志系统。
# 描述：实现支持多级别、多输出的日志系统。
# -----------------------------

import datetime

class Logger:
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    
    def __init__(self, name, level=INFO):
        self.name = name
        self.level = level
        self.handlers = []
    
    def add_handler(self, handler):
        self.handlers.append(handler)
    
    def log(self, level, message):
        if level >= self.level:
            record = {
                "name": self.name,
                "level": level,
                "message": message,
                "time": datetime.datetime.now()
            }
            for handler in self.handlers:
                handler.handle(record)
    
    def debug(self, message):
        self.log(self.DEBUG, message)
    
    def info(self, message):
        self.log(self.INFO, message)
    
    def warning(self, message):
        self.log(self.WARNING, message)
    
    def error(self, message):
        self.log(self.ERROR, message)

class ConsoleHandler:
    def handle(self, record):
        level_names = ["DEBUG", "INFO", "WARNING", "ERROR"]
        print(f"[{record['time']}] [{level_names[record['level']]}] {record['name']}: {record['message']}")

def main():
    logger = Logger("MyApp", Logger.DEBUG)
    logger.add_handler(ConsoleHandler())
    logger.info("应用启动")
    logger.warning("内存使用率较高")
    logger.error("连接超时")


if __name__ == "__main__":
    main()
