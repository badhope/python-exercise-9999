# -----------------------------
# 题目：实现CQRS框架。
# 描述：命令查询职责分离，读写分离架构。
# -----------------------------

from abc import ABC, abstractmethod
from typing import Dict, Any, Type, List, Callable
from dataclasses import dataclass

@dataclass
class Command:
    pass

@dataclass
class Query:
    pass

class CommandHandler(ABC):
    @abstractmethod
    def handle(self, command: Command) -> Any:
        pass

class QueryHandler(ABC):
    @abstractmethod
    def handle(self, query: Query) -> Any:
        pass

class CommandBus:
    def __init__(self):
        self.handlers: Dict[Type[Command], CommandHandler] = {}
    
    def register(self, command_type: Type[Command], handler: CommandHandler):
        self.handlers[command_type] = handler
    
    def dispatch(self, command: Command) -> Any:
        handler = self.handlers.get(type(command))
        if not handler:
            raise ValueError(f"未找到命令处理器: {type(command)}")
        return handler.handle(command)

class QueryBus:
    def __init__(self):
        self.handlers: Dict[Type[Query], QueryHandler] = {}
    
    def register(self, query_type: Type[Query], handler: QueryHandler):
        self.handlers[query_type] = handler
    
    def dispatch(self, query: Query) -> Any:
        handler = self.handlers.get(type(query))
        if not handler:
            raise ValueError(f"未找到查询处理器: {type(query)}")
        return handler.handle(query)

@dataclass
class CreateUserCommand(Command):
    user_id: str
    name: str
    email: str

@dataclass
class UpdateUserCommand(Command):
    user_id: str
    name: str = None
    email: str = None

@dataclass
class GetUserQuery(Query):
    user_id: str

@dataclass
class ListUsersQuery(Query):
    limit: int = 10

class UserWriteModel:
    def __init__(self):
        self.users: Dict[str, Dict[str, Any]] = {}
    
    def create(self, user_id: str, name: str, email: str):
        self.users[user_id] = {'id': user_id, 'name': name, 'email': email}
    
    def update(self, user_id: str, name: str = None, email: str = None):
        if user_id in self.users:
            if name:
                self.users[user_id]['name'] = name
            if email:
                self.users[user_id]['email'] = email

class UserReadModel:
    def __init__(self):
        self.users: Dict[str, Dict[str, Any]] = {}
    
    def get(self, user_id: str) -> Dict[str, Any]:
        return self.users.get(user_id)
    
    def list(self, limit: int) -> List[Dict[str, Any]]:
        return list(self.users.values())[:limit]
    
    def sync(self, users: Dict[str, Dict[str, Any]]):
        self.users = users.copy()

class CreateUserHandler(CommandHandler):
    def __init__(self, write_model: UserWriteModel, read_model: UserReadModel):
        self.write_model = write_model
        self.read_model = read_model
    
    def handle(self, command: CreateUserCommand) -> str:
        self.write_model.create(command.user_id, command.name, command.email)
        self.read_model.sync(self.write_model.users)
        return command.user_id

class UpdateUserHandler(CommandHandler):
    def __init__(self, write_model: UserWriteModel, read_model: UserReadModel):
        self.write_model = write_model
        self.read_model = read_model
    
    def handle(self, command: UpdateUserCommand) -> bool:
        self.write_model.update(command.user_id, command.name, command.email)
        self.read_model.sync(self.write_model.users)
        return True

class GetUserHandler(QueryHandler):
    def __init__(self, read_model: UserReadModel):
        self.read_model = read_model
    
    def handle(self, query: GetUserQuery) -> Dict[str, Any]:
        return self.read_model.get(query.user_id)

class ListUsersHandler(QueryHandler):
    def __init__(self, read_model: UserReadModel):
        self.read_model = read_model
    
    def handle(self, query: ListUsersQuery) -> List[Dict[str, Any]]:
        return self.read_model.list(query.limit)

def main():
    write_model = UserWriteModel()
    read_model = UserReadModel()
    
    command_bus = CommandBus()
    query_bus = QueryBus()
    
    command_bus.register(CreateUserCommand, CreateUserHandler(write_model, read_model))
    command_bus.register(UpdateUserCommand, UpdateUserHandler(write_model, read_model))
    query_bus.register(GetUserQuery, GetUserHandler(read_model))
    query_bus.register(ListUsersQuery, ListUsersHandler(read_model))
    
    command_bus.dispatch(CreateUserCommand("u1", "张三", "zhang@example.com"))
    command_bus.dispatch(CreateUserCommand("u2", "李四", "li@example.com"))
    command_bus.dispatch(UpdateUserCommand("u1", name="张三三"))
    
    user = query_bus.dispatch(GetUserQuery("u1"))
    users = query_bus.dispatch(ListUsersQuery(10))
    
    print(f"用户: {user}")
    print(f"用户列表: {users}")

if __name__ == "__main__":
    main()
