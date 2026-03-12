# -----------------------------
# 题目：实现查询构建器。
# 描述：支持链式查询、条件组合、SQL生成。
# -----------------------------

from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum

class JoinType(Enum):
    INNER = "INNER JOIN"
    LEFT = "LEFT JOIN"
    RIGHT = "RIGHT JOIN"
    CROSS = "CROSS JOIN"

class OrderDirection(Enum):
    ASC = "ASC"
    DESC = "DESC"

@dataclass
class WhereClause:
    column: str
    operator: str
    value: Any
    connector: str = "AND"

@dataclass
class JoinClause:
    join_type: JoinType
    table: str
    on_left: str
    on_right: str
    alias: Optional[str] = None

class QueryBuilder:
    def __init__(self, table: str = None):
        self._table = table
        self._alias: Optional[str] = None
        self._columns: List[str] = ["*"]
        self._wheres: List[WhereClause] = []
        self._joins: List[JoinClause] = []
        self._order_by: List[Tuple[str, OrderDirection]] = []
        self._group_by: List[str] = []
        self._having: List[WhereClause] = []
        self._limit: Optional[int] = None
        self._offset: Optional[int] = None
        self._distinct: bool = False
        self._params: List[Any] = []
    
    def table(self, table_name: str) -> 'QueryBuilder':
        self._table = table_name
        return self
    
    def from_(self, table_name: str) -> 'QueryBuilder':
        return self.table(table_name)
    
    def as_(self, alias: str) -> 'QueryBuilder':
        self._alias = alias
        return self
    
    def select(self, *columns: str) -> 'QueryBuilder':
        self._columns = list(columns) if columns else ["*"]
        return self
    
    def distinct(self) -> 'QueryBuilder':
        self._distinct = True
        return self
    
    def where(self, column: str, operator: str, value: Any) -> 'QueryBuilder':
        self._wheres.append(WhereClause(column, operator, value, "AND"))
        return self
    
    def where_eq(self, column: str, value: Any) -> 'QueryBuilder':
        return self.where(column, "=", value)
    
    def where_ne(self, column: str, value: Any) -> 'QueryBuilder':
        return self.where(column, "!=", value)
    
    def where_gt(self, column: str, value: Any) -> 'QueryBuilder':
        return self.where(column, ">", value)
    
    def where_gte(self, column: str, value: Any) -> 'QueryBuilder':
        return self.where(column, ">=", value)
    
    def where_lt(self, column: str, value: Any) -> 'QueryBuilder':
        return self.where(column, "<", value)
    
    def where_lte(self, column: str, value: Any) -> 'QueryBuilder':
        return self.where(column, "<=", value)
    
    def where_like(self, column: str, pattern: str) -> 'QueryBuilder':
        return self.where(column, "LIKE", pattern)
    
    def where_in(self, column: str, values: List[Any]) -> 'QueryBuilder':
        placeholders = ", ".join(["?" for _ in values])
        self._wheres.append(WhereClause(column, f"IN ({placeholders})", values, "AND"))
        return self
    
    def where_null(self, column: str) -> 'QueryBuilder':
        self._wheres.append(WhereClause(column, "IS NULL", None, "AND"))
        return self
    
    def where_not_null(self, column: str) -> 'QueryBuilder':
        self._wheres.append(WhereClause(column, "IS NOT NULL", None, "AND"))
        return self
    
    def or_where(self, column: str, operator: str, value: Any) -> 'QueryBuilder':
        self._wheres.append(WhereClause(column, operator, value, "OR"))
        return self
    
    def join(self, table: str, left: str, right: str, alias: str = None) -> 'QueryBuilder':
        self._joins.append(JoinClause(JoinType.INNER, table, left, right, alias))
        return self
    
    def left_join(self, table: str, left: str, right: str, alias: str = None) -> 'QueryBuilder':
        self._joins.append(JoinClause(JoinType.LEFT, table, left, right, alias))
        return self
    
    def right_join(self, table: str, left: str, right: str, alias: str = None) -> 'QueryBuilder':
        self._joins.append(JoinClause(JoinType.RIGHT, table, left, right, alias))
        return self
    
    def order_by(self, column: str, direction: OrderDirection = OrderDirection.ASC) -> 'QueryBuilder':
        self._order_by.append((column, direction))
        return self
    
    def order_by_desc(self, column: str) -> 'QueryBuilder':
        return self.order_by(column, OrderDirection.DESC)
    
    def group_by(self, *columns: str) -> 'QueryBuilder':
        self._group_by.extend(columns)
        return self
    
    def having(self, column: str, operator: str, value: Any) -> 'QueryBuilder':
        self._having.append(WhereClause(column, operator, value, "AND"))
        return self
    
    def limit(self, limit: int) -> 'QueryBuilder':
        self._limit = limit
        return self
    
    def offset(self, offset: int) -> 'QueryBuilder':
        self._offset = offset
        return self
    
    def paginate(self, page: int, per_page: int) -> 'QueryBuilder':
        self._limit = per_page
        self._offset = (page - 1) * per_page
        return self
    
    def build_select(self) -> Tuple[str, List[Any]]:
        self._params = []
        
        sql_parts = []
        
        select_clause = "SELECT "
        if self._distinct:
            select_clause += "DISTINCT "
        select_clause += ", ".join(self._columns)
        sql_parts.append(select_clause)
        
        from_clause = f"FROM {self._table}"
        if self._alias:
            from_clause += f" AS {self._alias}"
        sql_parts.append(from_clause)
        
        for join in self._joins:
            join_clause = f"{join.join_type.value} {join.table}"
            if join.alias:
                join_clause += f" AS {join.alias}"
            join_clause += f" ON {join.on_left} = {join.on_right}"
            sql_parts.append(join_clause)
        
        if self._wheres:
            where_parts = []
            for i, w in enumerate(self._wheres):
                if i == 0:
                    where_parts.append(f"{w.column} {w.operator}")
                else:
                    where_parts.append(f"{w.connector} {w.column} {w.operator}")
                
                if w.value is not None:
                    if isinstance(w.value, list):
                        self._params.extend(w.value)
                    else:
                        self._params.append(w.value)
            
            sql_parts.append("WHERE " + " ".join(where_parts))
        
        if self._group_by:
            sql_parts.append("GROUP BY " + ", ".join(self._group_by))
        
        if self._having:
            having_parts = []
            for h in self._having:
                having_parts.append(f"{h.column} {h.operator}")
                if h.value is not None:
                    self._params.append(h.value)
            sql_parts.append("HAVING " + " AND ".join(having_parts))
        
        if self._order_by:
            order_parts = [f"{col} {dir.value}" for col, dir in self._order_by]
            sql_parts.append("ORDER BY " + ", ".join(order_parts))
        
        if self._limit is not None:
            sql_parts.append(f"LIMIT {self._limit}")
        
        if self._offset is not None:
            sql_parts.append(f"OFFSET {self._offset}")
        
        return " ".join(sql_parts), self._params
    
    def build_insert(self, data: Dict[str, Any]) -> Tuple[str, List[Any]]:
        columns = list(data.keys())
        placeholders = ", ".join(["?" for _ in columns])
        
        sql = f"INSERT INTO {self._table} ({', '.join(columns)}) VALUES ({placeholders})"
        params = list(data.values())
        
        return sql, params
    
    def build_update(self, data: Dict[str, Any]) -> Tuple[str, List[Any]]:
        set_parts = [f"{col} = ?" for col in data.keys()]
        params = list(data.values())
        
        sql = f"UPDATE {self._table} SET {', '.join(set_parts)}"
        
        if self._wheres:
            where_parts = []
            for i, w in enumerate(self._wheres):
                if i == 0:
                    where_parts.append(f"{w.column} {w.operator}")
                else:
                    where_parts.append(f"{w.connector} {w.column} {w.operator}")
                
                if w.value is not None:
                    if isinstance(w.value, list):
                        params.extend(w.value)
                    else:
                        params.append(w.value)
            
            sql += " WHERE " + " ".join(where_parts)
        
        return sql, params
    
    def build_delete(self) -> Tuple[str, List[Any]]:
        sql = f"DELETE FROM {self._table}"
        params = []
        
        if self._wheres:
            where_parts = []
            for i, w in enumerate(self._wheres):
                if i == 0:
                    where_parts.append(f"{w.column} {w.operator}")
                else:
                    where_parts.append(f"{w.connector} {w.column} {w.operator}")
                
                if w.value is not None:
                    if isinstance(w.value, list):
                        params.extend(w.value)
                    else:
                        params.append(w.value)
            
            sql += " WHERE " + " ".join(where_parts)
        
        return sql, params

def main():
    print("=== SELECT 查询 ===")
    sql, params = (QueryBuilder("users")
        .select("id", "username", "email")
        .where_eq("status", "active")
        .where_gt("age", 18)
        .where_like("email", "%@example.com")
        .order_by_desc("created_at")
        .limit(10)
        .build_select())
    print(f"SQL: {sql}")
    print(f"参数: {params}")
    
    print("\n=== JOIN 查询 ===")
    sql, params = (QueryBuilder("orders")
        .select("orders.id", "users.username", "orders.amount")
        .join("users", "orders.user_id", "users.id")
        .where_eq("orders.status", "completed")
        .order_by("orders.created_at", OrderDirection.DESC)
        .paginate(1, 20)
        .build_select())
    print(f"SQL: {sql}")
    print(f"参数: {params}")
    
    print("\n=== INSERT 查询 ===")
    sql, params = (QueryBuilder("users")
        .build_insert({
            "username": "zhangsan",
            "email": "zhang@example.com",
            "age": 25
        }))
    print(f"SQL: {sql}")
    print(f"参数: {params}")
    
    print("\n=== UPDATE 查询 ===")
    sql, params = (QueryBuilder("users")
        .where_eq("id", 1)
        .build_update({
            "username": "lisi",
            "age": 30
        }))
    print(f"SQL: {sql}")
    print(f"参数: {params}")
    
    print("\n=== DELETE 查询 ===")
    sql, params = (QueryBuilder("users")
        .where_eq("id", 1)
        .build_delete())
    print(f"SQL: {sql}")
    print(f"参数: {params}")

if __name__ == "__main__":
    main()
