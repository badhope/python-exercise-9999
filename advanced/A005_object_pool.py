# -----------------------------
# 题目：实现简单的对象池。
# 描述：重用对象以减少创建开销。
# -----------------------------

class PooledObject:
    def __init__(self, obj_id):
        self.obj_id = obj_id
        self.data = None
    
    def reset(self):
        self.data = None
    
    def process(self, data):
        self.data = data
        return f"Object-{self.obj_id} 处理: {data}"

class ObjectPool:
    def __init__(self, factory, max_size=10):
        self.factory = factory
        self.max_size = max_size
        self.available = []
        self.in_use = set()
        self.lock = threading.Lock()
    
    def acquire(self):
        with self.lock:
            if self.available:
                obj = self.available.pop()
            elif len(self.in_use) < self.max_size:
                obj = self.factory()
            else:
                raise Exception("对象池已满")
            self.in_use.add(obj)
            return obj
    
    def release(self, obj):
        with self.lock:
            if obj in self.in_use:
                self.in_use.remove(obj)
                obj.reset()
                self.available.append(obj)
    
    def get_stats(self):
        return {
            "available": len(self.available),
            "in_use": len(self.in_use)
        }

def main():
    counter = [0]
    def create_object():
        counter[0] += 1
        return PooledObject(counter[0])
    
    pool = ObjectPool(create_object, 3)
    obj1 = pool.acquire()
    obj2 = pool.acquire()
    print(obj1.process("任务A"))
    pool.release(obj1)
    print(f"池状态: {pool.get_stats()}")


if __name__ == "__main__":
    main()
