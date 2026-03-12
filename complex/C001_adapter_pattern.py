# -----------------------------
# 题目：适配器模式实现日志系统。
# 描述：使用适配器模式统一不同日志库的接口。
# -----------------------------

class Logger:
    def log(self, message):
        raise NotImplementedError

class ConsoleLogger(Logger):
    def log(self, message):
        print(f"[Console] {message}")

class FileLogger(Logger):
    def __init__(self, filename):
        self.filename = filename
    
    def log(self, message):
        with open(self.filename, 'a') as f:
            f.write(f"{message}\n")

class ThirdPartyLogger:
    def write_message(self, msg, level):
        print(f"[ThirdParty-{level}] {msg}")

class ThirdPartyAdapter(Logger):
    def __init__(self, third_party):
        self.third_party = third_party
    
    def log(self, message):
        self.third_party.write_message(message, "INFO")

def main():
    loggers = [
        ConsoleLogger(),
        ThirdPartyAdapter(ThirdPartyLogger())
    ]
    for logger in loggers:
        logger.log("系统启动")


if __name__ == "__main__":
    main()
