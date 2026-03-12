# -----------------------------
# 题目：实现内存数据库。
# -----------------------------

class MemoryDatabase:
    def __init__(self):
        self.tables = {}
        self.indexes = {}
        self.auto_increment = {}
    
    def create_table(self, table_name, columns, primary_key='id'):
        self.tables[table_name] = {
            'columns': columns,
            'primary_key': primary_key,
            'data': {},
            'next_id': 1
        }
        self.indexes[table_name] = {}
        self.auto_increment[table_name] = 1
    
    def insert(self, table_name, record):
        if table_name not in self.tables:
            raise ValueError(f"表 {table_name} 不存在")
        
        table = self.tables[table_name]
        pk = table['primary_key']
        
        if pk not in record:
            record[pk] = self.auto_increment[table_name]
            self.auto_increment[table_name] += 1
        
        record_id = record[pk]
        table['data'][record_id] = record
        
        for col, value in record.items():
            if col not in self.indexes[table_name]:
                self.indexes[table_name][col] = {}
            if value not in self.indexes[table_name][col]:
                self.indexes[table_name][col][value] = set()
            self.indexes[table_name][col][value].add(record_id)
        
        return record_id
    
    def select(self, table_name, conditions=None):
        if table_name not in self.tables:
            raise ValueError(f"表 {table_name} 不存在")
        
        table = self.tables[table_name]
        
        if not conditions:
            return list(table['data'].values())
        
        result_ids = None
        for col, value in conditions.items():
            if col in self.indexes[table_name] and value in self.indexes[table_name][col]:
                ids = self.indexes[table_name][col][value]
                if result_ids is None:
                    result_ids = ids.copy()
                else:
                    result_ids &= ids
        
        if result_ids is None:
            return []
        
        return [table['data'][rid] for rid in result_ids]
    
    def update(self, table_name, conditions, updates):
        records = self.select(table_name, conditions)
        table = self.tables[table_name]
        pk = table['primary_key']
        
        for record in records:
            record_id = record[pk]
            for col, value in updates.items():
                if col in record and col != pk:
                    old_value = record[col]
                    if old_value in self.indexes[table_name].get(col, {}):
                        self.indexes[table_name][col][old_value].discard(record_id)
                    
                    record[col] = value
                    
                    if col not in self.indexes[table_name]:
                        self.indexes[table_name][col] = {}
                    if value not in self.indexes[table_name][col]:
                        self.indexes[table_name][col][value] = set()
                    self.indexes[table_name][col][value].add(record_id)
        
        return len(records)
    
    def delete(self, table_name, conditions):
        records = self.select(table_name, conditions)
        table = self.tables[table_name]
        pk = table['primary_key']
        
        for record in records:
            record_id = record[pk]
            for col, value in record.items():
                if col in self.indexes[table_name] and value in self.indexes[table_name][col]:
                    self.indexes[table_name][col][value].discard(record_id)
            del table['data'][record_id]
        
        return len(records)
    
    def count(self, table_name, conditions=None):
        return len(self.select(table_name, conditions))

def main():
    db = MemoryDatabase()
    
    db.create_table('users', ['id', 'name', 'email', 'age'], 'id')
    
    print("=== 插入数据 ===")
    db.insert('users', {'name': '张三', 'email': 'zhang@example.com', 'age': 25})
    db.insert('users', {'name': '李四', 'email': 'li@example.com', 'age': 30})
    db.insert('users', {'name': '王五', 'email': 'wang@example.com', 'age': 25})
    
    print(f"用户总数: {db.count('users')}")
    
    print("\n=== 查询数据 ===")
    users_25 = db.select('users', {'age': 25})
    print(f"25岁用户: {[u['name'] for u in users_25]}")
    
    print("\n=== 更新数据 ===")
    updated = db.update('users', {'name': '张三'}, {'age': 26})
    print(f"更新记录数: {updated}")
    
    print("\n=== 删除数据 ===")
    deleted = db.delete('users', {'name': '李四'})
    print(f"删除记录数: {deleted}")
    print(f"剩余用户数: {db.count('users')}")


if __name__ == "__main__":
    main()
