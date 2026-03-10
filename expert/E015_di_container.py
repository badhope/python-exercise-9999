# -----------------------------
# 题目：实现简易依赖注入容器。
# -----------------------------

class Container:
    def __init__(self):
        self.services = {}
        self.instances = {}
    
    def register(self, service_name, factory, singleton=False):
        self.services[service_name] = {"factory": factory, "singleton": singleton}
    
    def resolve(self, service_name):
        if service_name not in self.services:
            raise ValueError(f"服务 {service_name} 未注册")
        service_info = self.services[service_name]
        if service_info["singleton"]:
            if service_name not in self.instances:
                self.instances[service_name] = service_info["factory"](self)
            return self.instances[service_name]
        return service_info["factory"](self)

class Database:
    def __init__(self, container):
        self.connection = f"db_connection_for_{id(self)}"

class UserService:
    def __init__(self, container):
        self.db = container.resolve("database")

def main():
    container = Container()
    container.register("database", lambda c: Database(c), singleton=True)
    container.register("user_service", lambda c: UserService(c))
    user_svc1 = container.resolve("user_service")
    user_svc2 = container.resolve("user_service")
    print(f"数据库实例相同: {user_svc1.db is user_svc2.db}")


if __name__ == "__main__":
    main()
