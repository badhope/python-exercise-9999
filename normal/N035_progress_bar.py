# -----------------------------
# 题目：实现简单的进度条。
# 描述：显示任务执行进度。
# -----------------------------

import sys
import time

class ProgressBar:
    def __init__(self, total, width=50, fill='█', empty='░'):
        self.total = total
        self.width = width
        self.fill = fill
        self.empty = empty
        self.current = 0
        self.start_time = None
    
    def start(self):
        self.current = 0
        self.start_time = time.time()
        self._display()
    
    def update(self, amount=1):
        self.current += amount
        self._display()
    
    def set_current(self, current):
        self.current = current
        self._display()
    
    def finish(self):
        self.current = self.total
        self._display()
        print()
    
    def _display(self):
        if self.total == 0:
            return
        
        percent = self.current / self.total
        filled_width = int(self.width * percent)
        bar = self.fill * filled_width + self.empty * (self.width - filled_width)
        
        elapsed = time.time() - self.start_time if self.start_time else 0
        if self.current > 0 and percent > 0:
            eta = elapsed / percent - elapsed
        else:
            eta = 0
        
        sys.stdout.write(f'\r[{bar}] {percent*100:.1f}% ({self.current}/{self.total}) '
                        f'耗时:{elapsed:.1f}s 剩余:{eta:.1f}s')
        sys.stdout.flush()
    
    def get_progress(self):
        return {
            'current': self.current,
            'total': self.total,
            'percent': self.current / self.total * 100 if self.total > 0 else 0,
            'elapsed': time.time() - self.start_time if self.start_time else 0
        }

class MultiProgressBar:
    def __init__(self, tasks):
        self.tasks = tasks
        self.bars = {}
        for task_id, (total, name) in tasks.items():
            self.bars[task_id] = {
                'total': total,
                'current': 0,
                'name': name
            }
    
    def update(self, task_id, amount=1):
        if task_id in self.bars:
            self.bars[task_id]['current'] += amount
            self._display()
    
    def _display(self):
        lines = []
        for task_id, bar in self.bars.items():
            percent = bar['current'] / bar['total'] if bar['total'] > 0 else 0
            filled = int(20 * percent)
            bar_str = '█' * filled + '░' * (20 - filled)
            lines.append(f'{bar["name"]}: [{bar_str}] {percent*100:.1f}%')
        
        sys.stdout.write('\r' + '\n'.join(lines))
        sys.stdout.flush()

def main():
    print("进度条演示:")
    bar = ProgressBar(100)
    bar.start()
    
    for i in range(100):
        time.sleep(0.02)
        bar.update()
    
    bar.finish()
    print("完成!")


if __name__ == "__main__":
    main()
