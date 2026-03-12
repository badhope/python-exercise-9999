# -----------------------------
# 题目：实现分布式ID生成器。
# 描述：支持雪花算法、唯一性保证、高性能生成。
# -----------------------------

import time
import threading
from typing import Optional
from datetime import datetime

class SnowflakeIdGenerator:
    def __init__(
        self,
        worker_id: int = 0,
        datacenter_id: int = 0,
        epoch: int = 1704067200000
    ):
        self.worker_id = worker_id
        self.datacenter_id = datacenter_id
        self.epoch = epoch
        
        self.worker_id_bits = 5
        self.datacenter_id_bits = 5
        self.sequence_bits = 12
        
        self.max_worker_id = (1 << self.worker_id_bits) - 1
        self.max_datacenter_id = (1 << self.datacenter_id_bits) - 1
        
        if worker_id > self.max_worker_id or worker_id < 0:
            raise ValueError(f"worker_id必须在0-{self.max_worker_id}之间")
        if datacenter_id > self.max_datacenter_id or datacenter_id < 0:
            raise ValueError(f"datacenter_id必须在0-{self.max_datacenter_id}之间")
        
        self.worker_id_shift = self.sequence_bits
        self.datacenter_id_shift = self.sequence_bits + self.worker_id_bits
        self.timestamp_left_shift = (
            self.sequence_bits + self.worker_id_bits + self.datacenter_id_bits
        )
        
        self.sequence_mask = (1 << self.sequence_bits) - 1
        
        self.sequence = 0
        self.last_timestamp = -1
        
        self._lock = threading.Lock()
    
    def next_id(self) -> int:
        with self._lock:
            timestamp = self._current_timestamp()
            
            if timestamp < self.last_timestamp:
                raise Exception(
                    f"时钟回拨: {self.last_timestamp - timestamp}毫秒"
                )
            
            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & self.sequence_mask
                if self.sequence == 0:
                    timestamp = self._wait_next_millis(self.last_timestamp)
            else:
                self.sequence = 0
            
            self.last_timestamp = timestamp
            
            return (
                ((timestamp - self.epoch) << self.timestamp_left_shift) |
                (self.datacenter_id << self.datacenter_id_shift) |
                (self.worker_id << self.worker_id_shift) |
                self.sequence
            )
    
    def _current_timestamp(self) -> int:
        return int(time.time() * 1000)
    
    def _wait_next_millis(self, last_timestamp: int) -> int:
        timestamp = self._current_timestamp()
        while timestamp <= last_timestamp:
            timestamp = self._current_timestamp()
        return timestamp
    
    def parse_id(self, id: int) -> dict:
        timestamp = (id >> self.timestamp_left_shift) + self.epoch
        datacenter_id = (id >> self.datacenter_id_shift) & self.max_datacenter_id
        worker_id = (id >> self.worker_id_shift) & self.max_worker_id
        sequence = id & self.sequence_mask
        
        return {
            'id': id,
            'timestamp': timestamp,
            'datetime': datetime.fromtimestamp(timestamp / 1000).isoformat(),
            'datacenter_id': datacenter_id,
            'worker_id': worker_id,
            'sequence': sequence
        }

class UUIDGenerator:
    @staticmethod
    def v1() -> str:
        import uuid
        return str(uuid.uuid1())
    
    @staticmethod
    def v4() -> str:
        import uuid
        return str(uuid.uuid4())
    
    @staticmethod
    def ordered() -> str:
        timestamp = int(time.time() * 1000000)
        import random
        random_part = random.randint(0, 0xFFFFFFFFFFFF)
        return f"{timestamp:016x}{random_part:012x}"

class ObjectIdGenerator:
    def __init__(self, machine_id: int = None):
        self.machine_id = machine_id or self._get_machine_id()
        self._counter = 0
        self._lock = threading.Lock()
    
    def _get_machine_id(self) -> int:
        import hashlib
        import socket
        hostname = socket.gethostname()
        return int(hashlib.md5(hostname.encode()).hexdigest()[:6], 16)
    
    def generate(self) -> str:
        with self._lock:
            timestamp = int(time.time())
            
            self._counter = (self._counter + 1) % 0xFFFFFF
            
            pid = self._get_process_id()
            
            oid = (
                (timestamp << 32) |
                (self.machine_id << 16) |
                (pid << 8) |
                self._counter
            )
            
            return format(oid, '024x')
    
    def _get_process_id(self) -> int:
        import os
        return os.getpid() % 0xFF
    
    def parse(self, oid: str) -> dict:
        value = int(oid, 16)
        
        timestamp = (value >> 32) & 0xFFFFFFFF
        machine_id = (value >> 16) & 0xFFFF
        process_id = (value >> 8) & 0xFF
        counter = value & 0xFF
        
        return {
            'oid': oid,
            'timestamp': timestamp,
            'datetime': datetime.fromtimestamp(timestamp).isoformat(),
            'machine_id': machine_id,
            'process_id': process_id,
            'counter': counter
        }

class DistributedIdService:
    def __init__(self, worker_id: int = 0, datacenter_id: int = 0):
        self.snowflake = SnowflakeIdGenerator(worker_id, datacenter_id)
        self.object_id = ObjectIdGenerator()
    
    def next_snowflake_id(self) -> int:
        return self.snowflake.next_id()
    
    def next_object_id(self) -> str:
        return self.object_id.generate()
    
    def next_uuid(self) -> str:
        return UUIDGenerator.v4()
    
    def next_ordered_id(self) -> str:
        return UUIDGenerator.ordered()
    
    def batch_generate(self, count: int, id_type: str = "snowflake") -> list:
        if id_type == "snowflake":
            return [self.next_snowflake_id() for _ in range(count)]
        elif id_type == "object_id":
            return [self.next_object_id() for _ in range(count)]
        elif id_type == "uuid":
            return [self.next_uuid() for _ in range(count)]
        return []

def main():
    generator = SnowflakeIdGenerator(worker_id=1, datacenter_id=1)
    
    print("生成10个雪花ID:")
    for i in range(10):
        id = generator.next_id()
        parsed = generator.parse_id(id)
        print(f"  ID: {id}")
        print(f"    时间: {parsed['datetime']}")
        print(f"    数据中心: {parsed['datacenter_id']}, 工作节点: {parsed['worker_id']}")
        print(f"    序列号: {parsed['sequence']}")
    
    service = DistributedIdService(worker_id=1)
    
    print("\n不同类型ID:")
    print(f"  雪花ID: {service.next_snowflake_id()}")
    print(f"  ObjectId: {service.next_object_id()}")
    print(f"  UUID: {service.next_uuid()}")
    print(f"  有序ID: {service.next_ordered_id()}")
    
    print("\n批量生成:")
    batch = service.batch_generate(5, "snowflake")
    print(f"  {batch}")

if __name__ == "__main__":
    main()
