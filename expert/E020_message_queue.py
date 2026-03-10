# -----------------------------
# 题目：实现消息队列。
# -----------------------------

import time
import threading
from collections import deque

class MessageQueue:
    def __init__(self):
        self.queue = deque()
        self.lock = threading.Lock()
        self.not_empty = threading.Condition(self.lock)
    
    def enqueue(self, message):
        with self.not_empty:
            self.queue.append(message)
            self.not_empty.notify()
    
    def dequeue(self, timeout=None):
        with self.not_empty:
            while not self.queue:
                if not self.not_empty.wait(timeout):
                    return None
            return self.queue.popleft()

def producer(queue, messages):
    for msg in messages:
        print(f"生产: {msg}")
        queue.enqueue(msg)
        time.sleep(0.5)

def consumer(queue):
    while True:
        msg = queue.dequeue(timeout=2)
        if msg:
            print(f"消费: {msg}")

def main():
    queue = MessageQueue()
    threading.Thread(target=producer, args=(queue, ["msg1", "msg2", "msg3"])).start()


if __name__ == "__main__":
    main()
