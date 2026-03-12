# -----------------------------
# 题目：实现上下文管理器高级版。
# -----------------------------

from typing import Any, Callable, Optional
from contextlib import contextmanager
import time

class ContextManager:
    def __init__(self, enter_func: Callable = None, exit_func: Callable = None):
        self._enter_func = enter_func
        self._exit_func = exit_func
    
    def __enter__(self):
        if self._enter_func:
            return self._enter_func()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._exit_func:
            return self._exit_func(exc_type, exc_val, exc_tb)
        return False

class Timer:
    def __init__(self, name: str = ""):
        self.name = name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        print(f"{self.name} 耗时: {duration:.4f}秒")
        return False

class SuppressExceptions:
    def __init__(self, *exceptions: type):
        self.exceptions = exceptions
        self.exception = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type and issubclass(exc_type, self.exceptions):
            self.exception = exc_val
            return True
        return False

class RedirectOutput:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.file = None
        self._original_stdout = None
    
    def __enter__(self):
        import sys
        self._original_stdout = sys.stdout
        self.file = open(self.filepath, 'w', encoding='utf-8')
        sys.stdout = self.file
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import sys
        sys.stdout = self._original_stdout
        if self.file:
            self.file.close()
        return False

class ChangeDirectory:
    def __init__(self, path: str):
        self.path = path
        self._original_path = None
    
    def __enter__(self):
        import os
        self._original_path = os.getcwd()
        os.chdir(self.path)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import os
        os.chdir(self._original_path)
        return False

class Lock:
    def __init__(self):
        import threading
        self._lock = threading.Lock()
    
    def __enter__(self):
        self._lock.acquire()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._lock.release()
        return False

class DatabaseTransaction:
    def __init__(self, connection):
        self.connection = connection
        self._committed = False
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        return False
    
    def commit(self):
        self._committed = True
        print("事务已提交")
    
    def rollback(self):
        print("事务已回滚")

@contextmanager
def measure_time(name: str = ""):
    start = time.time()
    yield
    end = time.time()
    print(f"{name} 耗时: {end - start:.4f}秒")

@contextmanager
def temporary_file(content: str = ""):
    import tempfile
    import os
    
    fd, path = tempfile.mkstemp()
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(content)
        yield path
    finally:
        os.unlink(path)

@contextmanager
def environment_variable(name: str, value: str):
    import os
    
    original = os.environ.get(name)
    os.environ[name] = value
    
    try:
        yield
    finally:
        if original is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = original

class NestedContext:
    def __init__(self):
        self._contexts = []
    
    def add(self, context_manager):
        self._contexts.append(context_manager)
        return self
    
    def __enter__(self):
        for ctx in self._contexts:
            ctx.__enter__()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        for ctx in reversed(self._contexts):
            ctx.__exit__(exc_type, exc_val, exc_tb)
        return False

def main():
    print("=== Timer上下文 ===")
    with Timer("计算"):
        sum(range(1000000))
    
    print("\n=== SuppressExceptions ===")
    with SuppressExceptions(ZeroDivisionError) as ctx:
        result = 1 / 0
    print(f"捕获异常: {ctx.exception}")
    
    print("\n=== measure_time装饰器 ===")
    with measure_time("排序"):
        sorted(range(10000, 0, -1))
    
    print("\n=== temporary_file ===")
    with temporary_file("临时内容") as path:
        print(f"临时文件路径: {path}")
        with open(path, 'r') as f:
            print(f"内容: {f.read()}")
    
    print("\n=== environment_variable ===")
    import os
    print(f"原始PATH: {os.environ.get('MY_VAR', '未设置')}")
    
    with environment_variable('MY_VAR', 'test_value'):
        print(f"设置后: {os.environ.get('MY_VAR')}")
    
    print(f"恢复后: {os.environ.get('MY_VAR', '未设置')}")
    
    print("\n=== NestedContext ===")
    nested = (NestedContext()
              .add(Timer("操作1"))
              .add(Timer("操作2")))
    
    with nested:
        sum(range(100000))


if __name__ == "__main__":
    main()
