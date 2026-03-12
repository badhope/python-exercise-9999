# -----------------------------
# 题目：实现简单的工作队列。
# 描述：使用队列实现任务分发。
# -----------------------------

import queue
import threading
import time

class Worker(threading.Thread):
    def __init__(self, work_queue, result_queue):
        super().__init__()
        self.work_queue = work_queue
        self.result_queue = result_queue
        self.daemon = True
    
    def run(self):
        while True:
            try:
                task = self.work_queue.get(timeout=1)
                if task is None:
                    break
                result = self.execute_task(task)
                self.result_queue.put(result)
            except queue.Empty:
                continue
    
    def execute_task(self, task):
        func, args = task
        return func(*args)

class WorkQueue:
    def __init__(self, num_workers=4):
        self.work_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.workers = []
        
        for _ in range(num_workers):
            worker = Worker(self.work_queue, self.result_queue)
            worker.start()
            self.workers.append(worker)
    
    def submit(self, func, *args):
        self.work_queue.put((func, args))
    
    def get_result(self, timeout=None):
        return self.result_queue.get(timeout=timeout)
    
    def shutdown(self):
        for _ in self.workers:
            self.work_queue.put(None)
        for worker in self.workers:
            worker.join()

def main():
    def task(n):
        time.sleep(0.1)
        return n ** 2
    
    wq = WorkQueue(3)
    for i in range(5):
        wq.submit(task, i)
    
    results = []
    for _ in range(5):
        results.append(wq.get_result())
    
    print(f"结果: {results}")
    wq.shutdown()


if __name__ == "__main__":
    main()
