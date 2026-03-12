# -----------------------------
# 题目：实现简单的线程池。
# 描述：管理线程的创建和任务执行。
# -----------------------------

import threading
import queue

class ThreadPool:
    def __init__(self, num_threads=4):
        self.num_threads = num_threads
        self.tasks = queue.Queue()
        self.workers = []
        self.running = True
        
        for _ in range(num_threads):
            worker = threading.Thread(target=self._worker)
            worker.daemon = True
            worker.start()
            self.workers.append(worker)
    
    def _worker(self):
        while self.running:
            try:
                task = self.tasks.get(timeout=1)
                if task:
                    func, args, kwargs, callback = task
                    result = func(*args, **kwargs)
                    if callback:
                        callback(result)
            except queue.Empty:
                continue
    
    def submit(self, func, *args, callback=None, **kwargs):
        self.tasks.put((func, args, kwargs, callback))
    
    def shutdown(self):
        self.running = False
        for worker in self.workers:
            worker.join()
    
    def get_pending_tasks(self):
        return self.tasks.qsize()

def main():
    pool = ThreadPool(2)
    
    def task(n):
        import time
        time.sleep(0.1)
        return n * 2
    
    def callback(result):
        print(f"结果: {result}")
    
    for i in range(5):
        pool.submit(task, i, callback=callback)
    
    import time
    time.sleep(1)
    pool.shutdown()


if __name__ == "__main__":
    main()
