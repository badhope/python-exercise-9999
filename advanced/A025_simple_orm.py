# -----------------------------
# 题目：实现简单的ORM映射器。
# -----------------------------

import re
from dataclasses import dataclass
from typing import Dict, List, Any, Type

@dataclass
class Column:
    name: str
    type: type
    primary_key: bool = False
    nullable: bool = True
    default: Any = None

class ModelMeta(type):
    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        
        if name != 'Model':
            cls._table_name = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
            cls._columns = {}
            cls._primary_key = None
            
            for key, value in namespace.items():
                if isinstance(value, Column):
                    cls._columns[key] = value
                    if value.primary_key:
                        cls._primary_key = key
        
        return cls

class Model(metaclass=ModelMeta):
    _table_name: str = None
    _columns: Dict[str, Column] = {}
    _primary_key: str = None
    
    def __init__(self, **kwargs):
        for key in self._columns:
            setattr(self, key, kwargs.get(key, self._columns[key].default))
    
    def to_dict(self) -> Dict:
        return {key: getattr(self, key) for key in self._columns}
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(**data)

class QueryBuilder:
    def __init__(self, model: Type[Model]):
        self.model = model
        self._where_conditions = []
        self._order_by = []
        self._limit = None
        self._offset = None
    
    def where(self, column: str, operator: str, value: Any):
        self._where_conditions.append((column, operator, value))
        return self
    
    def order_by(self, column: str, direction: str = 'ASC'):
        self._order_by.append((column, direction))
        return self
    
    def limit(self, limit: int):
        self._limit = limit
        return self
    
    def offset(self, offset: int):
        self._offset = offset
        return self
    
    def build_select(self) -> str:
        table = self.model._table_name
        columns = ', '.join(self.model._columns.keys())
        
        sql = f"SELECT {columns} FROM {table}"
        
        if self._where_conditions:
            conditions = []
            for col, op, val in self._where_conditions:
                conditions.append(f"{col} {op} %s")
            sql += " WHERE " + " AND ".join(conditions)
        
        if self._order_by:
            orders = [f"{col} {dir}" for col, dir in self._order_by]
            sql += " ORDER BY " + ", ".join(orders)
        
        if self._limit:
            sql += f" LIMIT {self._limit}"
        
        if self._offset:
            sql += f" OFFSET {self._offset}"
        
        return sql
    
    def get_params(self) -> List:
        return [val for _, _, val in self._where_conditions]

class Session:
    def __init__(self):
        self._new_objects = []
        self._dirty_objects = []
        self._deleted_objects = []
    
    def add(self, obj: Model):
        self._new_objects.append(obj)
    
    def delete(self, obj: Model):
        self._deleted_objects.append(obj)
    
    def commit(self):
        for obj in self._new_objects:
            self._insert(obj)
        
        for obj in self._dirty_objects:
            self._update(obj)
        
        for obj in self._deleted_objects:
            self._delete(obj)
        
        self._new_objects.clear()
        self._dirty_objects.clear()
        self._deleted_objects.clear()
    
    def _insert(self, obj: Model):
        table = obj._table_name
        columns = [k for k in obj._columns if k != obj._primary_key]
        values = [getattr(obj, k) for k in columns]
        
        sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
        print(f"执行SQL: {sql}")
        print(f"参数: {values}")
    
    def _update(self, obj: Model):
        table = obj._table_name
        columns = [k for k in obj._columns if k != obj._primary_key]
        pk = obj._primary_key
        
        set_clause = ', '.join([f"{k} = %s" for k in columns])
        sql = f"UPDATE {table} SET {set_clause} WHERE {pk} = %s"
        
        values = [getattr(obj, k) for k in columns]
        values.append(getattr(obj, pk))
        
        print(f"执行SQL: {sql}")
        print(f"参数: {values}")
    
    def _delete(self, obj: Model):
        table = obj._table_name
        pk = obj._primary_key
        
        sql = f"DELETE FROM {table} WHERE {pk} = %s"
        print(f"执行SQL: {sql}")
        print(f"参数: [{getattr(obj, pk)}]")

class User(Model):
    id = Column('id', int, primary_key=True)
    name = Column('name', str, nullable=False)
    email = Column('email', str, nullable=False)
    age = Column('age', int, default=0)

class Product(Model):
    id = Column('id', int, primary_key=True)
    name = Column('name', str, nullable=False)
    price = Column('price', float, default=0.0)

def main():
    print("=== 模型信息 ===")
    print(f"User表名: {User._table_name}")
    print(f"User列: {list(User._columns.keys())}")
    print(f"User主键: {User._primary_key}")
    
    print("\n=== 创建对象 ===")
    user = User(id=1, name='张三', email='zhang@example.com', age=25)
    print(f"用户数据: {user.to_dict()}")
    
    print("\n=== 查询构建 ===")
    query = QueryBuilder(User).where('age', '>', 18).order_by('name').limit(10)
    print(f"SQL: {query.build_select()}")
    print(f"参数: {query.get_params()}")
    
    print("\n=== 会话操作 ===")
    session = Session()
    
    new_user = User(name='李四', email='li@example.com', age=30)
    session.add(new_user)
    
    session.commit()


if __name__ == "__main__":
    main()
