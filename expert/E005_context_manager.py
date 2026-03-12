# -----------------------------
# 题目：实现上下文管理器。
# 描述：使用with语句管理资源。
# -----------------------------

import time

class Timer:
    def __enter__(self):
        self.start = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = time.time()
        self.elapsed = self.end - self.start
        print(f"耗时: {self.elapsed:.4f}秒")
        return False

class FileHandler:
    def __init__(self, filename, mode='r'):
        self.filename = filename
        self.mode = mode
        self.file = None
    
    def __enter__(self):
        self.file = open(self.filename, self.mode)
        return self.file
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()
        return False

from contextlib import contextmanager

@contextmanager
def temp_directory():
    import tempfile
    import shutil
    temp_dir = tempfile.mkdtemp()
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)

def main():
    with Timer():
        sum(range(1000000))
    
    with temp_directory() as tmpdir:
        print(f"临时目录: {tmpdir}")


if __name__ == "__main__":
    main()
