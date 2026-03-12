# -----------------------------
# 题目：责任链模式实现日志级别处理。
# -----------------------------

class Logger:
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    
    def __init__(self, level):
        self.level = level
        self.next_logger = None
    
    def set_next(self, logger):
        self.next_logger = logger
        return logger
    
    def log(self, level, message):
        if level >= self.level:
            self._write(message)
        if self.next_logger:
            self.next_logger.log(level, message)
    
    def _write(self, message):
        pass

class ConsoleLogger(Logger):
    def _write(self, message):
        print(f"[Console] {message}")

class FileLogger(Logger):
    def __init__(self, level, filename="app.log"):
        super().__init__(level)
        self.filename = filename
    
    def _write(self, message):
        with open(self.filename, 'a', encoding='utf-8') as f:
            f.write(f"{message}\n")

class ErrorAlertLogger(Logger):
    def _write(self, message):
        print(f"[ALERT] 发送错误通知: {message}")

class DatabaseLogger(Logger):
    def __init__(self, level):
        super().__init__(level)
        self.logs = []
    
    def _write(self, message):
        self.logs.append(message)

def main():
    console = ConsoleLogger(Logger.DEBUG)
    file_logger = FileLogger(Logger.INFO)
    db_logger = DatabaseLogger(Logger.WARNING)
    alert = ErrorAlertLogger(Logger.ERROR)
    
    console.set_next(file_logger).set_next(db_logger).set_next(alert)
    
    print("=== Debug消息 ===")
    console.log(Logger.DEBUG, "调试信息: 变量x=10")
    
    print("\n=== Info消息 ===")
    console.log(Logger.INFO, "系统信息: 用户登录成功")
    
    print("\n=== Warning消息 ===")
    console.log(Logger.WARNING, "警告: 内存使用率80%")
    
    print("\n=== Error消息 ===")
    console.log(Logger.ERROR, "错误: 数据库连接失败")
    
    print(f"\n数据库日志记录数: {len(db_logger.logs)}")


if __name__ == "__main__":
    main()
