# -----------------------------
# 题目：实现ORM框架。
# 描述：支持模型定义、查询构建、关系映射。
# -----------------------------

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Type, Callable, get_type_hints
from dataclasses import dataclass, field
import re

@dataclass
class Column:
    name: str
    type: str
    primary_key: bool = False
    nullable: bool = True
    default: Any = None
    auto_increment: bool = False

@dataclass
class TableSchema:
    table_name: str
    columns: Dict[str, Column]
    primary_key: str = None

class ModelMeta(type):
    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        
        if name == 'Model':
            return cls
        
        columns = {}
        primary_key = None
        
        for attr_name, attr_value in namespace.items():
            if isinstance(attr_value, Column):
                columns[attr_name] = attr_value
                if attr_value.primary_key:
                    primary_key = attr_name
        
        cls._schema = TableSchema(
            table_name=namespace.get('__table__', name.lower()),
            columns=columns,
            primary_key=primary_key or 'id'
        )
        
        return cls

class Model(metaclass=ModelMeta):
    _schema: TableSchema = None
    
    def __init__(self, **kwargs):
        for col_name in self._schema.columns:
            setattr(self, col_name, kwargs.get(col_name))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            col_name: getattr(self, col_name, None)
            for col_name in self._schema.columns
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Model':
        return cls(**data)

class QueryBuilder:
    def __init__(self, model: Type[Model]):
        self.model = model
        self._table = model._schema.table_name
        self._columns = ['*']
        self._where = []
        self._order_by = []
        self._limit = None
        self._offset = None
        self._params = []
    
    def select(self, *columns: str) -> 'QueryBuilder':
        self._columns = columns if columns else ['*']
        return self
    
    def where(self, condition: str, *params) -> 'QueryBuilder':
        self._where.append(condition)
        self._params.extend(params)
        return self
    
    def where_eq(self, column: str, value: Any) -> 'QueryBuilder':
        return self.where(f"{column} = ?", value)
    
    def where_in(self, column: str, values: List[Any]) -> 'QueryBuilder':
        placeholders = ', '.join(['?' for _ in values])
        return self.where(f"{column} IN ({placeholders})", *values)
    
    def where_like(self, column: str, pattern: str) -> 'QueryBuilder':
        return self.where(f"{column} LIKE ?", pattern)
    
    def order_by(self, column: str, direction: str = 'ASC') -> 'QueryBuilder':
        self._order_by.append(f"{column} {direction}")
        return self
    
    def limit(self, limit: int) -> 'QueryBuilder':
        self._limit = limit
        return self
    
    def offset(self, offset: int) -> 'QueryBuilder':
        self._offset = offset
        return self
    
    def build_select(self) -> tuple:
        sql = f"SELECT {', '.join(self._columns)} FROM {self._table}"
        
        if self._where:
            sql += f" WHERE {' AND '.join(self._where)}"
        
        if self._order_by:
            sql += f" ORDER BY {', '.join(self._order_by)}"
        
        if self._limit:
            sql += f" LIMIT {self._limit}"
        
        if self._offset:
            sql += f" OFFSET {self._offset}"
        
        return sql, self._params
    
    def build_insert(self, data: Dict[str, Any]) -> tuple:
        columns = list(data.keys())
        placeholders = ', '.join(['?' for _ in columns])
        
        sql = f"INSERT INTO {self._table} ({', '.join(columns)}) VALUES ({placeholders})"
        params = [data[col] for col in columns]
        
        return sql, params
    
    def build_update(self, data: Dict[str, Any]) -> tuple:
        set_clause = ', '.join([f"{col} = ?" for col in data.keys()])
        params = list(data.values())
        
        sql = f"UPDATE {self._table} SET {set_clause}"
        
        if self._where:
            sql += f" WHERE {' AND '.join(self._where)}"
            params.extend(self._params)
        
        return sql, params
    
    def build_delete(self) -> tuple:
        sql = f"DELETE FROM {self._table}"
        
        if self._where:
            sql += f" WHERE {' AND '.join(self._where)}"
        
        return sql, self._params

class Database:
    def __init__(self):
        self._tables: Dict[str, List[Dict]] = {}
        self._auto_increment: Dict[str, int] = {}
    
    def create_table(self, schema: TableSchema):
        self._tables[schema.table_name] = []
        self._auto_increment[schema.table_name] = 1
    
    def execute(self, sql: str, params: tuple = ()) -> Any:
        sql = sql.strip().upper()
        
        if sql.startswith('SELECT'):
            return self._execute_select(sql, params)
        elif sql.startswith('INSERT'):
            return self._execute_insert(sql, params)
        elif sql.startswith('UPDATE'):
            return self._execute_update(sql, params)
        elif sql.startswith('DELETE'):
            return self._execute_delete(sql, params)
    
    def _execute_select(self, sql: str, params: tuple) -> List[Dict]:
        table_match = re.search(r'FROM\s+(\w+)', sql, re.IGNORECASE)
        if not table_match:
            return []
        
        table_name = table_match.group(1).lower()
        rows = self._tables.get(table_name, [])
        
        if 'WHERE' in sql.upper():
            rows = self._apply_where(rows, sql, params)
        
        return rows
    
    def _execute_insert(self, sql: str, params: tuple) -> int:
        table_match = re.search(r'INTO\s+(\w+)', sql, re.IGNORECASE)
        if not table_match:
            return 0
        
        table_name = table_match.group(1).lower()
        
        columns_match = re.search(r'\(([^)]+)\)\s*VALUES', sql, re.IGNORECASE)
        if columns_match:
            columns = [c.strip() for c in columns_match.group(1).split(',')]
        else:
            columns = []
        
        row = dict(zip(columns, params))
        
        id_value = self._auto_increment.get(table_name, 1)
        if 'id' in columns:
            idx = columns.index('id')
            if params[idx] is None:
                row['id'] = id_value
                self._auto_increment[table_name] = id_value + 1
        else:
            row['id'] = id_value
            self._auto_increment[table_name] = id_value + 1
        
        self._tables[table_name].append(row)
        return row['id']
    
    def _execute_update(self, sql: str, params: tuple) -> int:
        return 0
    
    def _execute_delete(self, sql: str, params: tuple) -> int:
        return 0
    
    def _apply_where(self, rows: List[Dict], sql: str, params: tuple) -> List[Dict]:
        return rows

class ORM:
    def __init__(self, database: Database = None):
        self.database = database or Database()
    
    def register_model(self, model: Type[Model]):
        self.database.create_table(model._schema)
    
    def query(self, model: Type[Model]) -> QueryBuilder:
        return QueryBuilder(model)
    
    def save(self, model: Model) -> int:
        data = model.to_dict()
        builder = QueryBuilder(type(model))
        sql, params = builder.build_insert(data)
        return self.database.execute(sql, tuple(params))
    
    def find(self, model: Type[Model], id: int) -> Optional[Model]:
        builder = self.query(model).where_eq('id', id)
        sql, params = builder.build_select()
        results = self.database.execute(sql, tuple(params))
        
        if results:
            return model.from_dict(results[0])
        return None
    
    def find_all(self, model: Type[Model]) -> List[Model]:
        builder = self.query(model)
        sql, params = builder.build_select()
        results = self.database.execute(sql, tuple(params))
        return [model.from_dict(row) for row in results]

class User(Model):
    __table__ = 'users'
    
    id = Column('id', 'integer', primary_key=True, auto_increment=True)
    name = Column('name', 'varchar(100)')
    email = Column('email', 'varchar(200)')
    age = Column('age', 'integer', nullable=True)

def main():
    orm = ORM()
    orm.register_model(User)
    
    user1 = User(name="张三", email="zhang@example.com", age=25)
    user2 = User(name="李四", email="li@example.com", age=30)
    
    id1 = orm.save(user1)
    id2 = orm.save(user2)
    
    print(f"保存用户，ID: {id1}, {id2}")
    
    found = orm.find(User, 1)
    if found:
        print(f"查找用户: {found.to_dict()}")
    
    all_users = orm.find_all(User)
    print(f"所有用户: {[u.to_dict() for u in all_users]}")

if __name__ == "__main__":
    main()
