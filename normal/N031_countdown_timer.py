# -----------------------------
# 题目：实现简单的倒计时器。
# 描述：支持倒计时、暂停、继续功能。
# -----------------------------

import time

class CountdownTimer:
    def __init__(self):
        self.total_seconds = 0
        self.remaining = 0
        self.running = False
        self.paused = False
    
    def set_time(self, hours=0, minutes=0, seconds=0):
        self.total_seconds = hours * 3600 + minutes * 60 + seconds
        self.remaining = self.total_seconds
    
    def start(self):
        if self.remaining > 0:
            self.running = True
            self.paused = False
            self._run()
    
    def pause(self):
        self.paused = True
    
    def resume(self):
        if self.paused:
            self.paused = False
            self._run()
    
    def stop(self):
        self.running = False
        self.paused = False
        self.remaining = self.total_seconds
    
    def reset(self):
        self.running = False
        self.paused = False
        self.remaining = self.total_seconds
    
    def _run(self):
        while self.running and self.remaining > 0:
            if not self.paused:
                self._display()
                time.sleep(1)
                self.remaining -= 1
            else:
                time.sleep(0.1)
        
        if self.remaining == 0 and self.running:
            self._display()
            print("\n倒计时结束!")
            self.running = False
    
    def _display(self):
        hours = self.remaining // 3600
        minutes = (self.remaining % 3600) // 60
        seconds = self.remaining % 60
        print(f"\r倒计时: {hours:02d}:{minutes:02d}:{seconds:02d}", end="", flush=True)
    
    def get_remaining(self):
        return {
            'hours': self.remaining // 3600,
            'minutes': (self.remaining % 3600) // 60,
            'seconds': self.remaining % 60,
            'total_seconds': self.remaining
        }
    
    def get_progress(self):
        if self.total_seconds == 0:
            return 0
        return (self.total_seconds - self.remaining) / self.total_seconds * 100

def main():
    timer = CountdownTimer()
    timer.set_time(seconds=5)
    
    print("开始5秒倒计时...")
    timer.start()


if __name__ == "__main__":
    main()
