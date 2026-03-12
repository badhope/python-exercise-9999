# -----------------------------
# 题目：实现查询构建器。
# -----------------------------

import sqlite3

class QueryBuilder:
    def __init__(self, table):
        self.table = table
        self.select_columns = "*"
        self.where_conditions = []
        self.where_params = []
        self.order_by_column = None
        self.order_by_dir = "ASC"
        self.limit_count = None
        self.offset_count = None
        self.join_tables = []
        self.insert_data = {}
        self.update_data = {}
    
    def select(self, *columns):
        self.select_columns = ", ".join(columns) if columns else "*"
        return self
    
    def where(self, condition, *params):
        self.where_conditions.append(condition)
        self.where_params.extend(params)
        return self
    
    def order_by(self, column, direction="ASC"):
        self.order_by_column = column
        self.order_by_dir = direction
        return self
    
    def limit(self, count, offset=None):
        self.limit_count = count
        self.offset_count = offset
        return self
    
    def join(self, table, condition):
        self.join_tables.append((table, condition))
        return self
    
    def build_select(self):
        sql = f"SELECT {self.select_columns} FROM {self.table}"
        
        for table, condition in self.join_tables:
            sql += f" JOIN {table} ON {condition}"
        
        if self.where_conditions:
            sql += " WHERE " + " AND ".join(self.where_conditions)
        
        if self.order_by_column:
            sql += f" ORDER BY {self.order_by_column} {self.order_by_dir}"
        
        if self.limit_count:
            sql += f" LIMIT {self.limit_count}"
            if self.offset_count:
                sql += f" OFFSET {self.offset_count}"
        
        return sql, self.where_params
    
    def insert(self, data):
        self.insert_data = data
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in data])
        sql = f"INSERT INTO {self.table} ({columns}) VALUES ({placeholders})"
        return sql, list(data.values())
    
    def update(self, data):
        self.update_data = data
        sets = ", ".join([f"{k} = ?" for k in data.keys()])
        sql = f"UPDATE {self.table} SET {sets}"
        
        if self.where_conditions:
            sql += " WHERE " + " AND ".join(self.where_conditions)
        
        params = list(data.values()) + self.where_params
        return sql, params
    
    def delete(self):
        sql = f"DELETE FROM {self.table}"
        
        if self.where_conditions:
            sql += " WHERE " + " AND ".join(self.where_conditions)
        
        return sql, self.where_params

if __name__ == "__main__":
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")
    conn.execute("INSERT INTO users (name, age) VALUES ('Alice', 25)")
    conn.execute("INSERT INTO users (name, age) VALUES ('Bob', 30)")
    
    query = QueryBuilder("users")
    sql, params = query.select("name", "age").where("age > ?", 20).order_by("age").limit(10).build_select()
    print(f"Query: {sql}")
    print(f"Params: {params}")
    
    cursor = conn.execute(sql, params)
    print(f"Results: {cursor.fetchall()}")
