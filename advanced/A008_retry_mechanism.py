# -----------------------------
# 题目：实现简单的重试机制。
# 描述：支持失败重试、延迟重试。
# -----------------------------

import time
import random

class RetryPolicy:
    def __init__(self, max_retries=3, delay=1, backoff=2):
        self.max_retries = max_retries
        self.delay = delay
        self.backoff = backoff

def retry(policy=None):
    if policy is None:
        policy = RetryPolicy()
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            current_delay = policy.delay
            last_exception = None
            
            while retries <= policy.max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    retries += 1
                    if retries <= policy.max_retries:
                        print(f"重试 {retries}/{policy.max_retries}, 等待 {current_delay}秒")
                        time.sleep(current_delay)
                        current_delay *= policy.backoff
            
            raise last_exception
        return wrapper
    return decorator

@retry(RetryPolicy(max_retries=3, delay=0.5))
def unstable_function():
    if random.random() < 0.7:
        raise Exception("随机失败")
    return "成功"

def main():
    try:
        result = unstable_function()
        print(f"结果: {result}")
    except Exception as e:
        print(f"最终失败: {e}")


if __name__ == "__main__":
    main()
