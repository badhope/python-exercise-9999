# -----------------------------
# 题目：实现权限系统。
# -----------------------------

from enum import Enum

class Permission(Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"

class Role:
    def __init__(self, name, permissions=None):
        self.name = name
        self.permissions = permissions or []
    
    def has_permission(self, permission):
        return permission in self.permissions

class User:
    def __init__(self, user_id, name, roles=None):
        self.user_id = user_id
        self.name = name
        self.roles = roles or []
    
    def has_permission(self, permission):
        for role in self.roles:
            if role.has_permission(permission):
                return True
        return False

class PermissionSystem:
    def __init__(self):
        self.users = {}
        self.roles = {}
    
    def add_role(self, role):
        self.roles[role.name] = role
    
    def add_user(self, user):
        self.users[user.user_id] = user
    
    def assign_role(self, user_id, role_name):
        if user_id in self.users and role_name in self.roles:
            user = self.users[user_id]
            role = self.roles[role_name]
            if role not in user.roles:
                user.roles.append(role)
            return True
        return False
    
    def check_permission(self, user_id, permission):
        if user_id in self.users:
            return self.users[user_id].has_permission(permission)
        return False

if __name__ == "__main__":
    system = PermissionSystem()
    
    admin_role = Role("admin", [Permission.READ, Permission.WRITE, Permission.DELETE, Permission.ADMIN])
    user_role = Role("user", [Permission.READ, Permission.WRITE])
    guest_role = Role("guest", [Permission.READ])
    
    system.add_role(admin_role)
    system.add_role(user_role)
    system.add_role(guest_role)
    
    system.add_user(User("u1", "Alice"))
    system.add_user(User("u2", "Bob"))
    system.add_user(User("u3", "Charlie"))
    
    system.assign_role("u1", "admin")
    system.assign_role("u2", "user")
    system.assign_role("u3", "guest")
    
    print(f"Alice can delete: {system.check_permission('u1', Permission.DELETE)}")
    print(f"Bob can delete: {system.check_permission('u2', Permission.DELETE)}")
    print(f"Charlie can read: {system.check_permission('u3', Permission.READ)}")
