# -----------------------------
# 题目：代理模式实现访问控制。
# 描述：使用代理模式控制对敏感资源的访问。
# -----------------------------

class Resource:
    def access(self):
        return "访问敏感资源"

class ResourceProxy:
    def __init__(self, resource):
        self.resource = resource
        self.permissions = {}
    
    def grant_permission(self, user):
        self.permissions[user] = True
    
    def revoke_permission(self, user):
        self.permissions[user] = False
    
    def access(self, user):
        if self.permissions.get(user, False):
            return self.resource.access()
        return "拒绝访问：权限不足"

def main():
    resource = Resource()
    proxy = ResourceProxy(resource)
    
    proxy.grant_permission("admin")
    proxy.grant_permission("user1")
    
    print(f"admin: {proxy.access('admin')}")
    print(f"guest: {proxy.access('guest')}")
    
    proxy.revoke_permission("user1")
    print(f"user1: {proxy.access('user1')}")


if __name__ == "__main__":
    main()
