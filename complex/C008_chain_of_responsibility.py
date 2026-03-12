# -----------------------------
# 题目：责任链模式实现请求处理。
# 描述：使用责任链模式处理不同级别的请求。
# -----------------------------

class Handler:
    def __init__(self, level):
        self.level = level
        self.next_handler = None
    
    def set_next(self, handler):
        self.next_handler = handler
        return handler
    
    def handle(self, request_level, request):
        if request_level <= self.level:
            return self.process(request)
        elif self.next_handler:
            return self.next_handler.handle(request_level, request)
        return "无人处理该请求"
    
    def process(self, request):
        raise NotImplementedError

class ManagerHandler(Handler):
    def __init__(self):
        super().__init__(1)
    
    def process(self, request):
        return f"经理处理: {request}"

class DirectorHandler(Handler):
    def __init__(self):
        super().__init__(2)
    
    def process(self, request):
        return f"总监处理: {request}"

class CEOHandler(Handler):
    def __init__(self):
        super().__init__(3)
    
    def process(self, request):
        return f"CEO处理: {request}"

def main():
    manager = ManagerHandler()
    director = DirectorHandler()
    ceo = CEOHandler()
    
    manager.set_next(director).set_next(ceo)
    
    print(manager.handle(1, "请假1天"))
    print(manager.handle(2, "请假3天"))
    print(manager.handle(3, "请假7天"))


if __name__ == "__main__":
    main()
