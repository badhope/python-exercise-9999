# -----------------------------
# 题目：实现简单的命令总线。
# -----------------------------

from typing import Dict, Type, Any, Callable, List
from dataclasses import dataclass
from abc import ABC, abstractmethod

class Command(ABC):
    pass

class CommandHandler(ABC):
    @abstractmethod
    def handle(self, command: Command) -> Any:
        pass

class CommandResult:
    def __init__(self, success: bool, data: Any = None, error: str = None):
        self.success = success
        self.data = data
        self.error = error
    
    @classmethod
    def ok(cls, data: Any = None):
        return cls(True, data)
    
    @classmethod
    def fail(cls, error: str):
        return cls(False, error=error)

class CommandBus:
    def __init__(self):
        self._handlers: Dict[Type[Command], CommandHandler] = {}
        self._middleware: List[Callable] = []
    
    def register(self, command_type: Type[Command], handler: CommandHandler):
        self._handlers[command_type] = handler
    
    def register_callable(self, command_type: Type[Command], handler: Callable):
        class CallableHandler(CommandHandler):
            def handle(self, command):
                return handler(command)
        self._handlers[command_type] = CallableHandler()
    
    def add_middleware(self, middleware: Callable):
        self._middleware.append(middleware)
    
    def dispatch(self, command: Command) -> Any:
        command_type = type(command)
        
        if command_type not in self._handlers:
            raise ValueError(f"未找到命令处理器: {command_type.__name__}")
        
        for middleware in self._middleware:
            result = middleware(command)
            if result is not None:
                return result
        
        handler = self._handlers[command_type]
        return handler.handle(command)

class CommandDispatcher:
    def __init__(self, bus: CommandBus):
        self.bus = bus
    
    def dispatch(self, command: Command) -> Any:
        return self.bus.dispatch(command)

@dataclass
class CreateUserCommand(Command):
    name: str
    email: str

@dataclass
class UpdateUserCommand(Command):
    user_id: int
    name: str = None
    email: str = None

@dataclass
class DeleteUserCommand(Command):
    user_id: int

class CreateUserHandler(CommandHandler):
    def __init__(self):
        self.next_id = 1
        self.users: Dict[int, dict] = {}
    
    def handle(self, command: CreateUserCommand) -> CommandResult:
        user_id = self.next_id
        self.next_id += 1
        
        self.users[user_id] = {
            'id': user_id,
            'name': command.name,
            'email': command.email
        }
        
        return CommandResult.ok({'user_id': user_id})

class UpdateUserHandler(CommandHandler):
    def __init__(self, users: Dict[int, dict]):
        self.users = users
    
    def handle(self, command: UpdateUserCommand) -> CommandResult:
        if command.user_id not in self.users:
            return CommandResult.fail("用户不存在")
        
        user = self.users[command.user_id]
        if command.name:
            user['name'] = command.name
        if command.email:
            user['email'] = command.email
        
        return CommandResult.ok(user)

def logging_middleware(command: Command) -> Any:
    print(f"[LOG] 执行命令: {type(command).__name__}")
    return None

def validation_middleware(command: Command) -> Any:
    if hasattr(command, 'email') and command.email:
        if '@' not in command.email:
            return CommandResult.fail("邮箱格式无效")
    return None

def main():
    bus = CommandBus()
    bus.add_middleware(logging_middleware)
    bus.add_middleware(validation_middleware)
    
    create_handler = CreateUserHandler()
    bus.register(CreateUserCommand, create_handler)
    
    bus.register(UpdateUserCommand, UpdateUserHandler(create_handler.users))
    
    bus.register_callable(DeleteUserCommand, 
        lambda cmd: CommandResult.ok({'deleted': True, 'user_id': cmd.user_id}))
    
    print("=== 创建用户 ===")
    result = bus.dispatch(CreateUserCommand(name="张三", email="zhang@example.com"))
    print(f"结果: {result.success}, 数据: {result.data}")
    
    print("\n=== 更新用户 ===")
    result = bus.dispatch(UpdateUserCommand(user_id=1, name="李四"))
    print(f"结果: {result.success}, 数据: {result.data}")
    
    print("\n=== 删除用户 ===")
    result = bus.dispatch(DeleteUserCommand(user_id=1))
    print(f"结果: {result.success}, 数据: {result.data}")
    
    print("\n=== 验证失败 ===")
    result = bus.dispatch(CreateUserCommand(name="王五", email="invalid-email"))
    print(f"结果: {result.success}, 错误: {result.error}")


if __name__ == "__main__":
    main()
