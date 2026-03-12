# -----------------------------
# 题目：实现ORM框架。
# -----------------------------

import sqlite3

class ModelMeta(type):
    def __new__(mcs, name, bases, attrs):
        cls = super().__new__(mcs, name, bases, attrs)
        if hasattr(cls, '_table_name'):
            cls._fields = {k: v for k, v in attrs.items() if not k.startswith('_') and not callable(v)}
        return cls

class Model(metaclass=ModelMeta):
    _table_name = ""
    _connection = None
    
    @classmethod
    def set_connection(cls, conn):
        cls._connection = conn
    
    @classmethod
    def create_table(cls):
        if not cls._connection:
            raise ValueError("No database connection")
        
        columns = [f"{k} TEXT" for k in cls._fields.keys()]
        sql = f"CREATE TABLE IF NOT EXISTS {cls._table_name} (id INTEGER PRIMARY KEY, {', '.join(columns)})"
        cls._connection.execute(sql)
        cls._connection.commit()
    
    @classmethod
    def insert(cls, **kwargs):
        if not cls._connection:
            raise ValueError("No database connection")
        
        columns = ", ".join(kwargs.keys())
        placeholders = ", ".join(["?" for _ in kwargs])
        sql = f"INSERT INTO {cls._table_name} ({columns}) VALUES ({placeholders})"
        cursor = cls._connection.cursor()
        cursor.execute(sql, list(kwargs.values()))
        cls._connection.commit()
        return cursor.lastrowid
    
    @classmethod
    def all(cls):
        if not cls._connection:
            raise ValueError("No database connection")
        
        cursor = cls._connection.cursor()
        cursor.execute(f"SELECT * FROM {cls._table_name}")
        rows = cursor.fetchall()
        return [cls(**dict(zip(cls._fields.keys(), row[1:]))) for row in rows]

class User(Model):
    _table_name = "users"
    name = ""
    email = ""

if __name__ == "__main__":
    conn = sqlite3.connect(":memory:")
    User.set_connection(conn)
    
    User.create_table()
    User.insert(name="张三", email="zhangsan@example.com")
    User.insert(name="李四", email="lisi@example.com")
    
    users = User.all()
    for u in users:
        print(f"User: {u.name}, {u.email}")
