# -----------------------------
# 题目：实现简单的数据库迁移工具。
# 描述：支持版本管理和迁移执行。
# -----------------------------

class Migration:
    def __init__(self, version, name):
        self.version = version
        self.name = name
    
    def up(self):
        raise NotImplementedError
    
    def down(self):
        raise NotImplementedError

class MigrationManager:
    def __init__(self):
        self.migrations = []
        self.applied = set()
    
    def register(self, migration):
        self.migrations.append(migration)
        self.migrations.sort(key=lambda m: m.version)
    
    def migrate(self, target=None):
        for migration in self.migrations:
            if migration.version not in self.applied:
                if target is None or migration.version <= target:
                    print(f"执行迁移: {migration.version} - {migration.name}")
                    migration.up()
                    self.applied.add(migration.version)
    
    def rollback(self, steps=1):
        applied = [m for m in self.migrations if m.version in self.applied]
        applied.reverse()
        for migration in applied[:steps]:
            print(f"回滚迁移: {migration.version} - {migration.name}")
            migration.down()
            self.applied.remove(migration.version)
    
    def status(self):
        return {
            'total': len(self.migrations),
            'applied': len(self.applied),
            'pending': len(self.migrations) - len(self.applied)
        }

class CreateUsersTable(Migration):
    def __init__(self):
        super().__init__('001', 'create_users_table')
    
    def up(self):
        print("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
    
    def down(self):
        print("DROP TABLE users")

class CreatePostsTable(Migration):
    def __init__(self):
        super().__init__('002', 'create_posts_table')
    
    def up(self):
        print("CREATE TABLE posts (id INTEGER PRIMARY KEY, title TEXT, user_id INTEGER)")
    
    def down(self):
        print("DROP TABLE posts")

def main():
    manager = MigrationManager()
    manager.register(CreateUsersTable())
    manager.register(CreatePostsTable())
    
    print("迁移状态:", manager.status())
    manager.migrate()
    print("迁移后状态:", manager.status())
    manager.rollback(1)
    print("回滚后状态:", manager.status())


if __name__ == "__main__":
    main()
