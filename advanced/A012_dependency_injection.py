# -----------------------------
# 题目：实现简单的依赖注入。
# 描述：支持服务的注册和依赖解析。
# -----------------------------

class Container:
    def __init__(self):
        self.services = {}
        self.singletons = {}
    
    def register(self, name, factory, singleton=False):
        self.services[name] = {"factory": factory, "singleton": singleton}
    
    def resolve(self, name):
        if name not in self.services:
            raise ValueError(f"服务 {name} 未注册")
        
        service = self.services[name]
        
        if service["singleton"]:
            if name not in self.singletons:
                self.singletons[name] = service["factory"](self)
            return self.singletons[name]
        
        return service["factory"](self)
    
    def has(self, name):
        return name in self.services

class Database:
    def __init__(self, connection_string):
        self.connection_string = connection_string
    
    def query(self, sql):
        return f"执行查询: {sql}"

class UserRepository:
    def __init__(self, db):
        self.db = db
    
    def find_all(self):
        return self.db.query("SELECT * FROM users")

def main():
    container = Container()
    
    container.register("db", lambda c: Database("sqlite:///:memory:"), singleton=True)
    container.register("user_repo", lambda c: UserRepository(c.resolve("db")))
    
    repo = container.resolve("user_repo")
    print(repo.find_all())


if __name__ == "__main__":
    main()
