# -----------------------------
# 题目：实现简单的分布式ID生成器。
# 描述：支持雪花算法、ID解析。
# -----------------------------

import time
import threading

class SnowflakeGenerator:
    def __init__(self, worker_id=0, datacenter_id=0):
        self.worker_id = worker_id
        self.datacenter_id = datacenter_id
        
        self.sequence = 0
        self.last_timestamp = -1
        
        self._lock = threading.Lock()
        
        self.epoch = 1704067200000
        self.worker_id_bits = 5
        self.datacenter_id_bits = 5
        self.sequence_bits = 12
        
        self.max_worker_id = (1 << self.worker_id_bits) - 1
        self.max_datacenter_id = (1 << self.datacenter_id_bits) - 1
        self.sequence_mask = (1 << self.sequence_bits) - 1
        
        self.worker_id_shift = self.sequence_bits
        self.datacenter_id_shift = self.sequence_bits + self.worker_id_bits
        self.timestamp_shift = self.sequence_bits + self.worker_id_bits + self.datacenter_id_bits
    
    def _current_millis(self):
        return int(time.time() * 1000)
    
    def _wait_next_millis(self, last_timestamp):
        timestamp = self._current_millis()
        while timestamp <= last_timestamp:
            timestamp = self._current_millis()
        return timestamp
    
    def generate(self):
        with self._lock:
            timestamp = self._current_millis()
            
            if timestamp < self.last_timestamp:
                raise ValueError("时钟回拨")
            
            
            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & self.sequence_mask
                if self.sequence == 0:
                    timestamp = self._wait_next_millis(self.last_timestamp)
            else:
                self.sequence = 0
            
            self.last_timestamp = timestamp
            
            return ((timestamp - self.epoch) << self.timestamp_shift) | \
                   (self.datacenter_id << self.datacenter_id_shift) | \
                   (self.worker_id << self.worker_id_shift) | \
                   self.sequence
    
    def parse(self, snowflake_id):
        timestamp = (snowflake_id >> self.timestamp_shift) + self.epoch
        datacenter_id = (snowflake_id >> self.datacenter_id_shift) & self.max_datacenter_id
        worker_id = (snowflake_id >> self.worker_id_shift) & self.max_worker_id
        sequence = snowflake_id & self.sequence_mask
        
        return {
            'timestamp': timestamp,
            'datetime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp / 1000)),
            'datacenter_id': datacenter_id,
            'worker_id': worker_id,
            'sequence': sequence
        }

def main():
    generator = SnowflakeGenerator(worker_id=1, datacenter_id=1)
    
    ids = [generator.generate() for _ in range(5)]
    print("生成的ID:")
    for id_ in ids:
        print(f"  {id_}")
    
    print("\n解析第一个ID:")
    parsed = generator.parse(ids[0])
    for key, value in parsed.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
