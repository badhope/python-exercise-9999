# -----------------------------
# 题目：上下文管理器实现数据库连接。
# -----------------------------

import sqlite3

class DatabaseConnection:
    def __init__(self, db_name=":memory:"):
        self.db_name = db_name
        self.conn = None
    
    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        return self.conn
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
            self.conn.close()
        return False

def main():
    with DatabaseConnection(":memory:") as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
        cursor.execute("INSERT INTO users (name) VALUES ('张三')")
        cursor.execute("INSERT INTO users (name) VALUES ('李四')")
        cursor.execute("SELECT * FROM users")
        print("用户列表:")
        for row in cursor.fetchall():
            print(row)


if __name__ == "__main__":
    main()
