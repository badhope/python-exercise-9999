# -----------------------------
# 题目：实现ORM框架高级版。
# -----------------------------

from typing import Any, Dict, List, Optional, Type, Callable
from dataclasses import dataclass
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
class ForeignKey:
    column: str
    reference_table: str
    reference_column: str

class Table:
    def __init__(self, name: str):
        self.name = name
        self.columns: Dict[str, Column] = {}
        self.primary_key: str = None
        self.foreign_keys: List[ForeignKey] = []
    
    def add_column(self, column: Column):
        self.columns[column.name] = column
        if column.primary_key:
            self.primary_key = column.name
        return self
    
    def add_foreign_key(self, fk: ForeignKey):
        self.foreign_keys.append(fk)
        return self
    
    def create_sql(self) -> str:
        col_defs = []
        
        for col in self.columns.values():
            col_def = f"    {col.name} {col.type}"
            if col.primary_key:
                col_def += " PRIMARY KEY"
            if col.auto_increment:
                col_def += " AUTOINCREMENT"
            if not col.nullable:
                col_def += " NOT NULL"
            if col.default is not None:
                col_def += f" DEFAULT {col.default}"
            col_defs.append(col_def)
        
        for fk in self.foreign_keys:
            fk_def = f"    FOREIGN KEY ({fk.column}) REFERENCES {fk.reference_table}({fk.reference_column})"
            col_defs.append(fk_def)
        
        return f"CREATE TABLE {self.name} (\n" + ",\n".join(col_defs) + "\n);"

class QueryBuilder:
    def __init__(self, table: str):
        self.table = table
        self._columns: List[str] = []
        self._where: List[str] = []
        self._order_by: List[str] = []
        self._limit: int = None
        self._offset: int = None
        self._joins: List[str] = []
        self._group_by: List[str] = []
        self._having: List[str] = []
    
    def select(self, *columns: str) -> 'QueryBuilder':
        self._columns.extend(columns)
        return self
    
    def where(self, condition: str, *args) -> 'QueryBuilder':
        self._where.append((condition, args))
        return self
    
    def order_by(self, column: str, direction: str = 'ASC') -> 'QueryBuilder':
        self._order_by.append(f"{column} {direction}")
        return self
    
    def limit(self, limit: int) -> 'QueryBuilder':
        self._limit = limit
        return self
    
    def offset(self, offset: int) -> 'QueryBuilder':
        self._offset = offset
        return self
    
    def join(self, table: str, on: str, join_type: str = 'INNER') -> 'QueryBuilder':
        self._joins.append(f"{join_type} JOIN {table} ON {on}")
        return self
    
    def group_by(self, *columns: str) -> 'QueryBuilder':
        self._group_by.extend(columns)
        return self
    
    def having(self, condition: str) -> 'QueryBuilder':
        self._having.append(condition)
        return self
    
    def build(self) -> str:
        cols = ", ".join(self._columns) if self._columns else "*"
        sql = f"SELECT {cols} FROM {self.table}"
        
        for join in self._joins:
            sql += f" {join}"
        
        if self._where:
            conditions = [w[0] for w in self._where]
            sql += " WHERE " + " AND ".join(conditions)
        
        if self._group_by:
            sql += " GROUP BY " + ", ".join(self._group_by)
        
        if self._having:
            sql += " HAVING " + " AND ".join(self._having)
        
        if self._order_by:
            sql += " ORDER BY " + ", ".join(self._order_by)
        
        if self._limit:
            sql += f" LIMIT {self._limit}"
        
        if self._offset:
            sql += f" OFFSET {self._offset}"
        
        return sql + ";"

class InsertBuilder:
    def __init__(self, table: str):
        self.table = table
        self._data: Dict[str, Any] = {}
    
    def values(self, **kwargs) -> 'InsertBuilder':
        self._data.update(kwargs)
        return self
    
    def build(self) -> str:
        columns = ", ".join(self._data.keys())
        placeholders = ", ".join(["?"] * len(self._data))
        return f"INSERT INTO {self.table} ({columns}) VALUES ({placeholders});"
    
    def params(self) -> tuple:
        return tuple(self._data.values())

class UpdateBuilder:
    def __init__(self, table: str):
        self.table = table
        self._data: Dict[str, Any] = {}
        self._where: List[str] = []
    
    def set(self, **kwargs) -> 'UpdateBuilder':
        self._data.update(kwargs)
        return self
    
    def where(self, condition: str) -> 'UpdateBuilder':
        self._where.append(condition)
        return self
    
    def build(self) -> str:
        set_clause = ", ".join(f"{k} = ?" for k in self._data.keys())
        sql = f"UPDATE {self.table} SET {set_clause}"
        
        if self._where:
            sql += " WHERE " + " AND ".join(self._where)
        
        return sql + ";"
    
    def params(self) -> tuple:
        return tuple(self._data.values())

class DeleteBuilder:
    def __init__(self, table: str):
        self.table = table
        self._where: List[str] = []
    
    def where(self, condition: str) -> 'DeleteBuilder':
        self._where.append(condition)
        return self
    
    def build(self) -> str:
        sql = f"DELETE FROM {self.table}"
        
        if self._where:
            sql += " WHERE " + " AND ".join(self._where)
        
        return sql + ";"

class ModelMeta(type):
    def __new__(mcs, name: str, bases: tuple, namespace: dict):
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
    def query(cls) -> QueryBuilder:
        return QueryBuilder(cls._table_name)

def main():
    print("=== 表定义 ===")
    users = (Table("users")
             .add_column(Column("id", "INTEGER", primary_key=True, auto_increment=True))
             .add_column(Column("name", "VARCHAR(100)", nullable=False))
             .add_column(Column("email", "VARCHAR(255)"))
             .add_column(Column("created_at", "TIMESTAMP", default="CURRENT_TIMESTAMP")))
    
    print(users.create_sql())
    
    print("\n=== 查询构建 ===")
    query = (QueryBuilder("users")
             .select("id", "name", "email")
             .where("age > ?", 18)
             .where("status = ?", "active")
             .order_by("created_at", "DESC")
             .limit(10))
    
    print(query.build())
    
    print("\n=== 插入构建 ===")
    insert = (InsertBuilder("users")
              .values(name="张三", email="zhang@example.com", age=25))
    
    print(insert.build())
    print(f"参数: {insert.params()}")
    
    print("\n=== 更新构建 ===")
    update = (UpdateBuilder("users")
              .set(name="李四", age=26)
              .where("id = 1"))
    
    print(update.build())
    print(f"参数: {update.params()}")
    
    print("\n=== 删除构建 ===")
    delete = (DeleteBuilder("users")
              .where("id = 1"))
    
    print(delete.build())
    
    print("\n=== 连接查询 ===")
    join_query = (QueryBuilder("orders")
                  .select("orders.id", "users.name", "orders.total")
                  .join("users", "orders.user_id = users.id")
                  .where("orders.status = ?", "completed")
                  .order_by("orders.created_at", "DESC"))
    
    print(join_query.build())


if __name__ == "__main__":
    main()
