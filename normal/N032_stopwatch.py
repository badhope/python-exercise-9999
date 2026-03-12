# -----------------------------
# 题目：实现简单的秒表。
# 描述：支持计时、暂停、计圈功能。
# -----------------------------

import time

class Stopwatch:
    def __init__(self):
        self.start_time = None
        self.elapsed = 0
        self.running = False
        self.laps = []
    
    def start(self):
        if not self.running:
            self.start_time = time.time()
            self.running = True
    
    def stop(self):
        if self.running:
            self.elapsed += time.time() - self.start_time
            self.running = False
    
    def reset(self):
        self.start_time = None
        self.elapsed = 0
        self.running = False
        self.laps = []
    
    def lap(self):
        if self.running:
            current = self.get_elapsed()
            lap_time = current - sum(self.laps) if self.laps else current
            self.laps.append(lap_time)
            return lap_time
        return None
    
    def get_elapsed(self):
        if self.running:
            return self.elapsed + (time.time() - self.start_time)
        return self.elapsed
    
    def get_elapsed_formatted(self):
        elapsed = self.get_elapsed()
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        milliseconds = int((elapsed % 1) * 100)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:02d}"
    
    def get_laps(self):
        return self.laps
    
    def get_lap_times_formatted(self):
        return [self._format_time(lap) for lap in self.laps]
    
    def _format_time(self, seconds):
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        ms = int((seconds % 1) * 100)
        return f"{minutes:02d}:{secs:02d}.{ms:02d}"
    
    def get_best_lap(self):
        if not self.laps:
            return None
        return min(self.laps)
    
    def get_worst_lap(self):
        if not self.laps:
            return None
        return max(self.laps)
    
    def get_average_lap(self):
        if not self.laps:
            return None
        return sum(self.laps) / len(self.laps)

def main():
    sw = Stopwatch()
    
    print("秒表演示:")
    sw.start()
    time.sleep(0.5)
    
    print(f"计时: {sw.get_elapsed_formatted()}")
    time.sleep(0.3)
    
    lap1 = sw.lap()
    print(f"计圈1: {sw._format_time(lap1)}")
    time.sleep(0.2)
    
    lap2 = sw.lap()
    print(f"计圈2: {sw._format_time(lap2)}")
    
    sw.stop()
    print(f"总时间: {sw.get_elapsed_formatted()}")


if __name__ == "__main__":
    main()
