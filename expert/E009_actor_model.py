# -----------------------------
# 题目：实现简单的Actor模型。
# 描述：使用消息传递实现并发。
# -----------------------------

import threading
import queue
import time

class Actor:
    def __init__(self):
        self.mailbox = queue.Queue()
        self.running = False
        self.thread = None
    
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
    
    def send(self, message):
        self.mailbox.put(message)
    
    def _run(self):
        while self.running:
            try:
                message = self.mailbox.get(timeout=0.1)
                self.receive(message)
            except queue.Empty:
                continue
    
    def receive(self, message):
        raise NotImplementedError

class CounterActor(Actor):
    def __init__(self):
        super().__init__()
        self.count = 0
    
    def receive(self, message):
        if message["type"] == "increment":
            self.count += message["value"]
        elif message["type"] == "get":
            message["reply_to"].put(self.count)

class PrinterActor(Actor):
    def receive(self, message):
        print(f"[Printer] {message}")

def main():
    counter = CounterActor()
    printer = PrinterActor()
    
    counter.start()
    printer.start()
    
    counter.send({"type": "increment", "value": 5})
    counter.send({"type": "increment", "value": 3})
    
    result_queue = queue.Queue()
    counter.send({"type": "get", "reply_to": result_queue})
    
    time.sleep(0.2)
    count = result_queue.get()
    printer.send(f"计数器值: {count}")
    
    counter.stop()
    printer.stop()


if __name__ == "__main__":
    main()
