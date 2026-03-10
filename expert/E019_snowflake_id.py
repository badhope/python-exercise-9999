# -----------------------------
# 题目：实现分布式ID生成器。
# -----------------------------

import time
import random

class Snowflake:
    def __init__(self, worker_id=1, datacenter_id=1):
        self.worker_id = worker_id
        self.datacenter_id = datacenter_id
        self.sequence = 0
        self.last_timestamp = -1
    
    def generate_id(self):
        timestamp = self._current_timestamp()
        if timestamp < self.last_timestamp:
            raise Exception("时钟回拨")
        if timestamp == self.last_timestamp:
            self.sequence = (self.sequence + 1) & 4095
        else:
            self.sequence = 0
        self.last_timestamp = timestamp
        return ((timestamp - 1288834974657) << 22) | \
               (self.datacenter_id << 17) | \
               (self.worker_id << 12) | \
               self.sequence
    
    def _current_timestamp(self):
        return int(time.time() * 1000)

def main():
    snowflake = Snowflake(1, 1)
    ids = [snowflake.generate_id() for _ in range(5)]
    print("生成的ID:")
    for i, id_val in enumerate(ids, 1):
        print(f"  ID {i}: {id_val}")


if __name__ == "__main__":
    main()
