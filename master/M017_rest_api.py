# -----------------------------
# 题目：实现简单REST API框架。
# -----------------------------

class RestAPI:
    def __init__(self):
        self.routes = {}
    
    def route(self, path, methods=None):
        if methods is None:
            methods = ["GET"]
        def decorator(func):
            self.routes[(path, tuple(methods))] = func
            return func
        return decorator
    
    def handle(self, path, method):
        key = (path, method)
        if key in self.routes:
            return self.routes[key]()
        return {"error": "Not Found"}, 404

api = RestAPI()

@api.route("/users", methods=["GET"])
def get_users():
    return {"users": [{"id": 1, "name": "张三"}, {"id": 2, "name": "李四"}]}

@api.route("/users", methods=["POST"])
def create_user():
    return {"message": "用户创建成功", "id": 3}, 201

def main():
    response, status = api.handle("/users", "GET")
    print(f"GET /users: {response}")
    response, status = api.handle("/users", "POST")
    print(f"POST /users: {response}")
    response, status = api.handle("/users", "DELETE")
    print(f"DELETE /users: {response}")


if __name__ == "__main__":
    main()
