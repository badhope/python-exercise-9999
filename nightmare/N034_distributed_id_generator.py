# -----------------------------
# 题目：实现分布式ID生成器。
# 描述：支持Snowflake算法、UUID、分布式序号。
# -----------------------------

import time
import threading
import uuid
import hashlib
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SnowflakeConfig:
    worker_id: int = 0
    datacenter_id: int = 0
    epoch: int = 1704067200000
    worker_id_bits: int = 5
    datacenter_id_bits: int = 5
    sequence_bits: int = 12

class SnowflakeGenerator:
    def __init__(self, config: SnowflakeConfig = None):
        self.config = config or SnowflakeConfig()
        
        self._worker_id_shift = self.config.sequence_bits
        self._datacenter_id_shift = self.config.sequence_bits + self.config.worker_id_bits
        self._timestamp_left_shift = (
            self.config.sequence_bits +
            self.config.worker_id_bits +
            self.config.datacenter_id_bits
        )
        
        self._sequence_mask = (1 << self.config.sequence_bits) - 1
        self._max_worker_id = (1 << self.config.worker_id_bits) - 1
        self._max_datacenter_id = (1 << self.config.datacenter_id_bits) - 1
        
        if self.config.worker_id > self._max_worker_id:
            raise ValueError(f"Worker ID 超出范围: {self._max_worker_id}")
        
        if self.config.datacenter_id > self._max_datacenter_id:
            raise ValueError(f"Datacenter ID 超出范围: {self._max_datacenter_id}")
        
        self._sequence = 0
        self._last_timestamp = -1
        self._lock = threading.Lock()
    
    def next_id(self) -> int:
        with self._lock:
            timestamp = self._current_timestamp()
            
            if timestamp < self._last_timestamp:
                raise Exception(f"时钟回拨: {self._last_timestamp - timestamp}ms")
            
            if timestamp == self._last_timestamp:
                self._sequence = (self._sequence + 1) & self._sequence_mask
                if self._sequence == 0:
                    timestamp = self._wait_next_millis(self._last_timestamp)
            else:
                self._sequence = 0
            
            self._last_timestamp = timestamp
            
            return (
                ((timestamp - self.config.epoch) << self._timestamp_left_shift) |
                (self.config.datacenter_id << self._datacenter_id_shift) |
                (self.config.worker_id << self._worker_id_shift) |
                self._sequence
            )
    
    def _current_timestamp(self) -> int:
        return int(time.time() * 1000)
    
    def _wait_next_millis(self, last_timestamp: int) -> int:
        timestamp = self._current_timestamp()
        while timestamp <= last_timestamp:
            timestamp = self._current_timestamp()
        return timestamp
    
    def parse_id(self, id: int) -> Dict[str, Any]:
        timestamp = (id >> self._timestamp_left_shift) + self.config.epoch
        datacenter_id = (id >> self._datacenter_id_shift) & self._max_datacenter_id
        worker_id = (id >> self._worker_id_shift) & self._max_worker_id
        sequence = id & self._sequence_mask
        
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
        return str(uuid.uuid1())
    
    @staticmethod
    def v4() -> str:
        return str(uuid.uuid4())
    
    @staticmethod
    def v5(namespace: str, name: str) -> str:
        ns = uuid.UUID(namespace)
        return str(uuid.uuid5(ns, name))
    
    @staticmethod
    def short() -> str:
        return uuid.uuid4().hex[:12]

class ObjectIdGenerator:
    def __init__(self):
        self._counter = 0
        self._lock = threading.Lock()
    
    def generate(self) -> str:
        with self._lock:
            timestamp = int(time.time())
            self._counter = (self._counter + 1) % 0xFFFFFF
            
            return (
                f"{timestamp:08x}"
                f"{uuid.uuid4().hex[:16]}"
                f"{self._counter:06x}"
            )

class DistributedSequenceGenerator:
    def __init__(self, prefix: str = "", step: int = 1000):
        self.prefix = prefix
        self.step = step
        self._current = 0
        self._max = 0
        self._lock = threading.Lock()
    
    def next(self) -> str:
        with self._lock:
            if self._current >= self._max:
                self._allocate_range()
            
            self._current += 1
            return f"{self.prefix}{self._current}"
    
    def _allocate_range(self):
        self._current = self._max
        self._max += self.step

class IDGeneratorRegistry:
    def __init__(self):
        self._generators: Dict[str, Any] = {}
    
    def register_snowflake(self, name: str, worker_id: int, datacenter_id: int):
        config = SnowflakeConfig(worker_id=worker_id, datacenter_id=datacenter_id)
        self._generators[name] = SnowflakeGenerator(config)
    
    def register_sequence(self, name: str, prefix: str = ""):
        self._generators[name] = DistributedSequenceGenerator(prefix)
    
    def generate(self, name: str) -> Any:
        generator = self._generators.get(name)
        if generator:
            return generator.next_id() if isinstance(generator, SnowflakeGenerator) else generator.next()
        return None

def main():
    print("=== Snowflake ID ===")
    snowflake = SnowflakeGenerator(SnowflakeConfig(worker_id=1, datacenter_id=1))
    
    for i in range(5):
        id = snowflake.next_id()
        parsed = snowflake.parse_id(id)
        print(f"ID: {id}")
        print(f"  解析: {parsed['datetime']}, worker={parsed['worker_id']}, seq={parsed['sequence']}")
    
    print("\n=== UUID ===")
    print(f"UUID v4: {UUIDGenerator.v4()}")
    print(f"Short UUID: {UUIDGenerator.short()}")
    
    print("\n=== ObjectId ===")
    oid_gen = ObjectIdGenerator()
    for i in range(3):
        print(f"ObjectId: {oid_gen.generate()}")
    
    print("\n=== 分布式序号 ===")
    seq_gen = DistributedSequenceGenerator(prefix="ORD-")
    for i in range(5):
        print(f"序号: {seq_gen.next()}")
    
    print("\n=== ID注册表 ===")
    registry = IDGeneratorRegistry()
    registry.register_snowflake("user", worker_id=1, datacenter_id=1)
    registry.register_sequence("order", "ORD-")
    
    print(f"用户ID: {registry.generate('user')}")
    print(f"订单ID: {registry.generate('order')}")

if __name__ == "__main__":
    main()
