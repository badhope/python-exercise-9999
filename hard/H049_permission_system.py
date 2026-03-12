# -----------------------------
# 题目：实现简单的权限管理系统。
# 描述：管理用户、角色、权限等。
# -----------------------------

from datetime import datetime

class Permission:
    def __init__(self, permission_id, name, resource, action):
        self.id = permission_id
        self.name = name
        self.resource = resource
        self.action = action

class Role:
    def __init__(self, role_id, name, description=""):
        self.id = role_id
        self.name = name
        self.description = description
        self.permissions = []
        self.created_at = datetime.now()
    
    def add_permission(self, permission_id):
        if permission_id not in self.permissions:
            self.permissions.append(permission_id)
            return True
        return False
    
    def remove_permission(self, permission_id):
        if permission_id in self.permissions:
            self.permissions.remove(permission_id)
            return True
        return False
    
    def has_permission(self, permission_id):
        return permission_id in self.permissions

class User:
    def __init__(self, user_id, username, email):
        self.id = user_id
        self.username = username
        self.email = email
        self.roles = []
        self.status = "active"
        self.created_at = datetime.now()
    
    def assign_role(self, role_id):
        if role_id not in self.roles:
            self.roles.append(role_id)
            return True
        return False
    
    def remove_role(self, role_id):
        if role_id in self.roles:
            self.roles.remove(role_id)
            return True
        return False
    
    def has_role(self, role_id):
        return role_id in self.roles

class PermissionSystem:
    def __init__(self):
        self.permissions = {}
        self.roles = {}
        self.users = {}
        self.next_permission_id = 1
        self.next_role_id = 1
        self.next_user_id = 1
    
    def create_permission(self, name, resource, action):
        permission = Permission(self.next_permission_id, name, resource, action)
        self.permissions[self.next_permission_id] = permission
        self.next_permission_id += 1
        return permission.id
    
    def create_role(self, name, description=""):
        role = Role(self.next_role_id, name, description)
        self.roles[self.next_role_id] = role
        self.next_role_id += 1
        return role.id
    
    def create_user(self, username, email):
        user = User(self.next_user_id, username, email)
        self.users[self.next_user_id] = user
        self.next_user_id += 1
        return user.id
    
    def grant_permission_to_role(self, role_id, permission_id):
        role = self.roles.get(role_id)
        if role:
            return role.add_permission(permission_id)
        return False
    
    def revoke_permission_from_role(self, role_id, permission_id):
        role = self.roles.get(role_id)
        if role:
            return role.remove_permission(permission_id)
        return False
    
    def assign_role_to_user(self, user_id, role_id):
        user = self.users.get(user_id)
        if user:
            return user.assign_role(role_id)
        return False
    
    def revoke_role_from_user(self, user_id, role_id):
        user = self.users.get(user_id)
        if user:
            return user.remove_role(role_id)
        return False
    
    def check_permission(self, user_id, resource, action):
        user = self.users.get(user_id)
        if not user or user.status != "active":
            return False
        
        for role_id in user.roles:
            role = self.roles.get(role_id)
            if role:
                for perm_id in role.permissions:
                    perm = self.permissions.get(perm_id)
                    if perm and perm.resource == resource and perm.action == action:
                        return True
        return False
    
    def get_user_permissions(self, user_id):
        user = self.users.get(user_id)
        if not user:
            return []
        
        permissions = []
        for role_id in user.roles:
            role = self.roles.get(role_id)
            if role:
                for perm_id in role.permissions:
                    perm = self.permissions.get(perm_id)
                    if perm and perm not in permissions:
                        permissions.append(perm)
        return permissions
    
    def get_user_roles(self, user_id):
        user = self.users.get(user_id)
        if user:
            return [self.roles[rid] for rid in user.roles if rid in self.roles]
        return []
    
    def get_role_permissions(self, role_id):
        role = self.roles.get(role_id)
        if role:
            return [self.permissions[pid] for pid in role.permissions if pid in self.permissions]
        return []
    
    def get_stats(self):
        return {
            'users': len(self.users),
            'roles': len(self.roles),
            'permissions': len(self.permissions),
            'active_users': sum(1 for u in self.users.values() if u.status == "active")
        }

def main():
    system = PermissionSystem()
    
    p1 = system.create_permission("查看用户", "user", "read")
    p2 = system.create_permission("创建用户", "user", "create")
    p3 = system.create_permission("删除用户", "user", "delete")
    p4 = system.create_permission("查看文章", "article", "read")
    p5 = system.create_permission("编辑文章", "article", "edit")
    
    admin_role = system.create_role("管理员", "系统管理员")
    editor_role = system.create_role("编辑", "内容编辑")
    viewer_role = system.create_role("访客", "普通访客")
    
    system.grant_permission_to_role(admin_role, p1)
    system.grant_permission_to_role(admin_role, p2)
    system.grant_permission_to_role(admin_role, p3)
    system.grant_permission_to_role(admin_role, p4)
    system.grant_permission_to_role(admin_role, p5)
    
    system.grant_permission_to_role(editor_role, p4)
    system.grant_permission_to_role(editor_role, p5)
    
    system.grant_permission_to_role(viewer_role, p4)
    
    u1 = system.create_user("张三", "zhangsan@example.com")
    u2 = system.create_user("李四", "lisi@example.com")
    
    system.assign_role_to_user(u1, admin_role)
    system.assign_role_to_user(u2, editor_role)
    
    print("权限系统统计:")
    stats = system.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print(f"\n用户{u1}权限检查:")
    print(f"  查看用户: {system.check_permission(u1, 'user', 'read')}")
    print(f"  删除用户: {system.check_permission(u1, 'user', 'delete')}")
    
    print(f"\n用户{u2}权限检查:")
    print(f"  查看文章: {system.check_permission(u2, 'article', 'read')}")
    print(f"  删除用户: {system.check_permission(u2, 'user', 'delete')}")


if __name__ == "__main__":
    main()
