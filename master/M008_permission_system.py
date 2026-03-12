# -----------------------------
# 题目：实现简单的权限系统。
# 描述：支持角色、权限、资源访问控制。
# -----------------------------

class Permission:
    def __init__(self, name, description=''):
        self.name = name
        self.description = description

class Role:
    def __init__(self, name):
        self.name = name
        self.permissions = set()
    
    def add_permission(self, permission):
        self.permissions.add(permission)
    
    def has_permission(self, permission):
        return permission in self.permissions

class User:
    def __init__(self, username):
        self.username = username
        self.roles = set()
    
    def add_role(self, role):
        self.roles.add(role)
    
    def has_permission(self, permission):
        for role in self.roles:
            if role.has_permission(permission):
                return True
        return False

class ACL:
    def __init__(self):
        self.roles = {}
        self.permissions = {}
    
    def create_permission(self, name, description=''):
        permission = Permission(name, description)
        self.permissions[name] = permission
        return permission
    
    def create_role(self, name):
        role = Role(name)
        self.roles[name] = role
        return role
    
    def grant(self, role_name, permission_name):
        if role_name in self.roles and permission_name in self.permissions:
            self.roles[role_name].add_permission(permission_name)

def permission_required(permission):
    def decorator(func):
        def wrapper(user, *args, **kwargs):
            if user.has_permission(permission):
                return func(user, *args, **kwargs)
            raise PermissionError(f"需要权限: {permission}")
        return wrapper
    return decorator

def main():
    acl = ACL()
    
    acl.create_permission('read', '读取权限')
    acl.create_permission('write', '写入权限')
    acl.create_permission('delete', '删除权限')
    
    admin = acl.create_role('admin')
    editor = acl.create_role('editor')
    viewer = acl.create_role('viewer')
    
    acl.grant('admin', 'read')
    acl.grant('admin', 'write')
    acl.grant('admin', 'delete')
    acl.grant('editor', 'read')
    acl.grant('editor', 'write')
    acl.grant('viewer', 'read')
    
    user = User('张三')
    user.add_role(editor)
    
    @permission_required('write')
    def edit_post(user, post_id):
        return f"编辑文章 {post_id}"
    
    print(edit_post(user, 1))


if __name__ == "__main__":
    main()
