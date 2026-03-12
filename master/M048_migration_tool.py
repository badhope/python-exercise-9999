# -----------------------------
# 题目：实现数据库迁移工具。
# -----------------------------

import sqlite3

class Migration:
    def __init__(self, version, up_sql, down_sql=None):
        self.version = version
        self.up_sql = up_sql
        self.down_sql = down_sql

class MigrationManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._init_table()
    
    def _init_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()
    
    def get_current_version(self):
        cursor = self.conn.execute("SELECT MAX(version) FROM schema_migrations")
        result = cursor.fetchone()[0]
        return result or 0
    
    def migrate_up(self, migrations):
        current = self.get_current_version()
        
        sorted_migrations = sorted([m for m in migrations if m.version > current], 
                                  key=lambda m: m.version)
        
        for migration in sorted_migrations:
            print(f"Applying migration {migration.version}...")
            self.conn.executescript(migration.up_sql)
            self.conn.execute("INSERT INTO schema_migrations (version) VALUES (?)", 
                             (migration.version,))
            self.conn.commit()
            print(f"Migration {migration.version} applied")
    
    def migrate_down(self, migrations, target_version):
        current = self.get_current_version()
        
        sorted_migrations = sorted([m for m in migrations if m.version > target_version],
                                  key=lambda m: m.version, reverse=True)
        
        for migration in sorted_migrations:
            if migration.down_sql:
                print(f"Reverting migration {migration.version}...")
                self.conn.executescript(migration.down_sql)
                self.conn.execute("DELETE FROM schema_migrations WHERE version = ?",
                                 (migration.version,))
                self.conn.commit()
                print(f"Migration {migration.version} reverted")
    
    def close(self):
        self.conn.close()

if __name__ == "__main__":
    migrations = [
        Migration(1, """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                email TEXT
            )
        """, "DROP TABLE users"),
        Migration(2, """
            CREATE TABLE posts (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                title TEXT,
                content TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """, "DROP TABLE posts"),
    ]
    
    manager = MigrationManager(":memory:")
    print(f"Current version: {manager.get_current_version()}")
    
    manager.migrate_up(migrations)
    print(f"New version: {manager.get_current_version()}")
    
    manager.close()
