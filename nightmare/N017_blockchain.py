# -----------------------------
# 题目：实现简易区块链。
# -----------------------------

import hashlib
import time
import json

class Block:
    def __init__(self, index, data, previous_hash):
        self.index = index
        self.timestamp = time.time()
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()
    
    def calculate_hash(self):
        content = f"{self.index}{self.timestamp}{json.dumps(self.data)}{self.previous_hash}"
        return hashlib.sha256(content.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
    
    def create_genesis_block(self):
        return Block(0, {"data": "Genesis Block"}, "0")
    
    def get_latest_block(self):
        return self.chain[-1]
    
    def add_block(self, data):
        new_block = Block(
            len(self.chain),
            data,
            self.get_latest_block().hash
        )
        self.chain.append(new_block)
    
    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
        return True

def main():
    blockchain = Blockchain()
    blockchain.add_block({"sender": "张三", "receiver": "李四", "amount": 10})
    blockchain.add_block({"sender": "李四", "receiver": "王五", "amount": 5})
    print("区块链验证:", blockchain.is_chain_valid())
    for block in blockchain.chain:
        print(f"区块 {block.index}: {block.hash[:20]}...")


if __name__ == "__main__":
    main()
