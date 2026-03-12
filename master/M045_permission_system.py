# -----------------------------
# 题目：实现权限管理系统。
# 描述：支持角色权限、资源访问控制、权限继承。
# -----------------------------

from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps

class Permission(Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"

@dataclass
class Resource:
    resource_id: str
    resource_type: str
    name: str
    parent_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Role:
    role_id: str
    name: str
    permissions: Dict[str, Set[Permission]] = field(default_factory=dict)
    inherits_from: Set[str] = field(default_factory=set)
    
    def add_permission(self, resource_type: str, permission: Permission):
        if resource_type not in self.permissions:
            self.permissions[resource_type] = set()
        self.permissions[resource_type].add(permission)
    
    def remove_permission(self, resource_type: str, permission: Permission):
        if resource_type in self.permissions:
            self.permissions[resource_type].discard(permission)
    
    def has_permission(self, resource_type: str, permission: Permission) -> bool:
        return permission in self.permissions.get(resource_type, set())

@dataclass
class User:
    user_id: str
    username: str
    roles: Set[str] = field(default_factory=set)
    direct_permissions: Dict[str, Set[Permission]] = field(default_factory=dict)
    
    def add_role(self, role_id: str):
        self.roles.add(role_id)
    
    def remove_role(self, role_id: str):
        self.roles.discard(role_id)
    
    def add_direct_permission(self, resource_type: str, permission: Permission):
        if resource_type not in self.direct_permissions:
            self.direct_permissions[resource_type] = set()
        self.direct_permissions[resource_type].add(permission)

class PermissionManager:
    def __init__(self):
        self._roles: Dict[str, Role] = {}
        self._users: Dict[str, User] = {}
        self._resources: Dict[str, Resource] = {}
    
    def create_role(self, role_id: str, name: str) -> Role:
        role = Role(role_id=role_id, name=name)
        self._roles[role_id] = role
        return role
    
    def get_role(self, role_id: str) -> Optional[Role]:
        return self._roles.get(role_id)
    
    def create_user(self, user_id: str, username: str) -> User:
        user = User(user_id=user_id, username=username)
        self._users[user_id] = user
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        return self._users.get(user_id)
    
    def create_resource(self, resource_id: str, resource_type: str, name: str, parent_id: str = None) -> Resource:
        resource = Resource(
            resource_id=resource_id,
            resource_type=resource_type,
            name=name,
            parent_id=parent_id
        )
        self._resources[resource_id] = resource
        return resource
    
    def get_resource(self, resource_id: str) -> Optional[Resource]:
        return self._resources.get(resource_id)
    
    def check_permission(
        self,
        user_id: str,
        resource_type: str,
        permission: Permission
    ) -> bool:
        user = self._users.get(user_id)
        if not user:
            return False
        
        if resource_type in user.direct_permissions:
            if permission in user.direct_permissions[resource_type]:
                return True
        
        for role_id in user.roles:
            if self._check_role_permission(role_id, resource_type, permission):
                return True
        
        return False
    
    def _check_role_permission(
        self,
        role_id: str,
        resource_type: str,
        permission: Permission,
        visited: Set[str] = None
    ) -> bool:
        if visited is None:
            visited = set()
        
        if role_id in visited:
            return False
        visited.add(role_id)
        
        role = self._roles.get(role_id)
        if not role:
            return False
        
        if role.has_permission(resource_type, permission):
            return True
        
        for parent_role_id in role.inherits_from:
            if self._check_role_permission(parent_role_id, resource_type, permission, visited):
                return True
        
        return False
    
    def get_user_permissions(self, user_id: str) -> Dict[str, Set[Permission]]:
        user = self._users.get(user_id)
        if not user:
            return {}
        
        result: Dict[str, Set[Permission]] = {}
        
        for resource_type, perms in user.direct_permissions.items():
            if resource_type not in result:
                result[resource_type] = set()
            result[resource_type].update(perms)
        
        for role_id in user.roles:
            role_perms = self._get_role_permissions(role_id)
            for resource_type, perms in role_perms.items():
                if resource_type not in result:
                    result[resource_type] = set()
                result[resource_type].update(perms)
        
        return result
    
    def _get_role_permissions(
        self,
        role_id: str,
        visited: Set[str] = None
    ) -> Dict[str, Set[Permission]]:
        if visited is None:
            visited = set()
        
        if role_id in visited:
            return {}
        visited.add(role_id)
        
        role = self._roles.get(role_id)
        if not role:
            return {}
        
        result = {rt: perms.copy() for rt, perms in role.permissions.items()}
        
        for parent_role_id in role.inherits_from:
            parent_perms = self._get_role_permissions(parent_role_id, visited)
            for resource_type, perms in parent_perms.items():
                if resource_type not in result:
                    result[resource_type] = set()
                result[resource_type].update(perms)
        
        return result
    
    def grant_role(self, user_id: str, role_id: str) -> bool:
        user = self._users.get(user_id)
        role = self._roles.get(role_id)
        
        if user and role:
            user.add_role(role_id)
            return True
        return False
    
    def revoke_role(self, user_id: str, role_id: str) -> bool:
        user = self._users.get(user_id)
        if user:
            user.remove_role(role_id)
            return True
        return False

def require_permission(resource_type: str, permission: Permission, manager: PermissionManager):
    def decorator(func):
        @wraps(func)
        def wrapper(user_id: str, *args, **kwargs):
            if not manager.check_permission(user_id, resource_type, permission):
                raise PermissionError(f"用户 {user_id} 没有 {resource_type}:{permission.value} 权限")
            return func(user_id, *args, **kwargs)
        return wrapper
    return decorator

def main():
    pm = PermissionManager()
    
    admin_role = pm.create_role("admin", "管理员")
    admin_role.add_permission("user", Permission.READ)
    admin_role.add_permission("user", Permission.WRITE)
    admin_role.add_permission("user", Permission.DELETE)
    admin_role.add_permission("order", Permission.READ)
    admin_role.add_permission("order", Permission.WRITE)
    
    user_role = pm.create_role("user", "普通用户")
    user_role.add_permission("order", Permission.READ)
    user_role.inherits_from.add("guest")
    
    guest_role = pm.create_role("guest", "访客")
    guest_role.add_permission("order", Permission.READ)
    
    user1 = pm.create_user("u1", "张三")
    user1.add_role("admin")
    
    user2 = pm.create_user("u2", "李四")
    user2.add_role("user")
    
    user3 = pm.create_user("u3", "王五")
    
    print("权限检查:")
    print(f"张三读取用户: {pm.check_permission('u1', 'user', Permission.READ)}")
    print(f"张三删除用户: {pm.check_permission('u1', 'user', Permission.DELETE)}")
    print(f"李四读取订单: {pm.check_permission('u2', 'order', Permission.READ)}")
    print(f"李四写入用户: {pm.check_permission('u2', 'user', Permission.WRITE)}")
    print(f"王五读取订单: {pm.check_permission('u3', 'order', Permission.READ)}")
    
    print(f"\n张三的所有权限: {pm.get_user_permissions('u1')}")
    print(f"李四的所有权限: {pm.get_user_permissions('u2')}")

if __name__ == "__main__":
    main()
