# -----------------------------
# 题目：实现分布式ID生成器。
# -----------------------------

import time
import threading

class SnowflakeID:
    def __init__(self, worker_id=1, datacenter_id=1):
        self.worker_id = worker_id
        self.datacenter_id = datacenter_id
        self.sequence = 0
        self.last_timestamp = 0
        self.lock = threading.Lock()
        
        self.worker_id_bits = 5
        self.datacenter_id_bits = 5
        self.sequence_bits = 12
        
        self.max_worker_id = -1 ^ (-1 << self.worker_id_bits)
        self.max_datacenter_id = -1 ^ (-1 << self.datacenter_id_bits)
        
        self.worker_id_shift = self.sequence_bits
        self.datacenter_id_shift = self.sequence_bits + self.worker_id_bits
        self.timestamp_left_shift = self.sequence_bits + self.worker_id_bits + self.datacenter_id_bits
        self.sequence_mask = -1 ^ (-1 << self.sequence_bits)
    
    def generate(self):
        timestamp = self._current_timestamp()
        
        with self.lock:
            if timestamp < self.last_timestamp:
                raise Exception("Clock moved backwards")
            
            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & self.sequence_mask
                if self.sequence == 0:
                    timestamp = self._wait_next_timestamp()
            else:
                self.sequence = 0
            
            self.last_timestamp = timestamp
        
        return ((timestamp << self.timestamp_left_shift) |
                (self.datacenter_id << self.datacenter_id_shift) |
                (self.worker_id << self.worker_id_shift) |
                self.sequence)
    
    def _current_timestamp(self):
        return int(time.time() * 1000)
    
    def _wait_next_timestamp(self):
        timestamp = self._current_timestamp()
        while timestamp <= self.last_timestamp:
            timestamp = self._current_timestamp()
        return timestamp

if __name__ == "__main__":
    id_gen = SnowflakeID(worker_id=1, datacenter_id=1)
    
    ids = [id_gen.generate() for _ in range(5)]
    print(f"Generated IDs: {ids}")
    print(f"Unique: {len(set(ids)) == len(ids)}")
