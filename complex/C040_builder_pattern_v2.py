# -----------------------------
# 题目：建造者模式实现SQL查询构建器。
# -----------------------------

class SQLQueryBuilder:
    def __init__(self):
        self._table = None
        self._columns = []
        self._where_conditions = []
        self._join_clauses = []
        self._order_by = []
        self._group_by = []
        self._having_conditions = []
        self._limit = None
        self._offset = None
    
    def select(self, *columns):
        self._columns = list(columns)
        return self
    
    def from_table(self, table, alias=None):
        self._table = f"{table} AS {alias}" if alias else table
        return self
    
    def where(self, condition, *args):
        self._where_conditions.append((condition, args))
        return self
    
    def and_where(self, condition, *args):
        self._where_conditions.append(('AND ' + condition, args))
        return self
    
    def or_where(self, condition, *args):
        self._where_conditions.append(('OR ' + condition, args))
        return self
    
    def join(self, table, on, alias=None):
        table_str = f"{table} AS {alias}" if alias else table
        self._join_clauses.append(f"JOIN {table_str} ON {on}")
        return self
    
    def left_join(self, table, on, alias=None):
        table_str = f"{table} AS {alias}" if alias else table
        self._join_clauses.append(f"LEFT JOIN {table_str} ON {on}")
        return self
    
    def order_by(self, column, direction="ASC"):
        self._order_by.append(f"{column} {direction}")
        return self
    
    def group_by(self, *columns):
        self._group_by.extend(columns)
        return self
    
    def having(self, condition):
        self._having_conditions.append(condition)
        return self
    
    def limit(self, limit):
        self._limit = limit
        return self
    
    def offset(self, offset):
        self._offset = offset
        return self
    
    def build(self):
        parts = []
        
        columns = ', '.join(self._columns) if self._columns else '*'
        parts.append(f"SELECT {columns}")
        
        if self._table:
            parts.append(f"FROM {self._table}")
        
        for join in self._join_clauses:
            parts.append(join)
        
        if self._where_conditions:
            where_parts = []
            for i, (condition, args) in enumerate(self._where_conditions):
                if i == 0:
                    where_parts.append(condition.lstrip('AND ').lstrip('OR '))
                else:
                    where_parts.append(condition)
            parts.append("WHERE " + ' '.join(where_parts))
        
        if self._group_by:
            parts.append("GROUP BY " + ', '.join(self._group_by))
        
        if self._having_conditions:
            parts.append("HAVING " + ' AND '.join(self._having_conditions))
        
        if self._order_by:
            parts.append("ORDER BY " + ', '.join(self._order_by))
        
        if self._limit is not None:
            parts.append(f"LIMIT {self._limit}")
        
        if self._offset is not None:
            parts.append(f"OFFSET {self._offset}")
        
        return ' '.join(parts) + ';'

class InsertBuilder:
    def __init__(self):
        self._table = None
        self._columns = []
        self._values = []
    
    def into(self, table):
        self._table = table
        return self
    
    def columns(self, *columns):
        self._columns = list(columns)
        return self
    
    def values(self, *values):
        self._values = list(values)
        return self
    
    def build(self):
        columns = ', '.join(self._columns)
        placeholders = ', '.join(['%s'] * len(self._values))
        return f"INSERT INTO {self._table} ({columns}) VALUES ({placeholders});"

class UpdateBuilder:
    def __init__(self):
        self._table = None
        self._set_values = {}
        self._where_conditions = []
    
    def table(self, table):
        self._table = table
        return self
    
    def set(self, **kwargs):
        self._set_values.update(kwargs)
        return self
    
    def where(self, condition):
        self._where_conditions.append(condition)
        return self
    
    def build(self):
        set_clause = ', '.join([f"{k} = %s" for k in self._set_values.keys()])
        where_clause = ' AND '.join(self._where_conditions)
        return f"UPDATE {self._table} SET {set_clause} WHERE {where_clause};"

def main():
    print("=== SELECT查询 ===")
    query = (SQLQueryBuilder()
             .select('u.id', 'u.name', 'o.order_id', 'o.total')
             .from_table('users', 'u')
             .left_join('orders', 'o', 'o.user_id = u.id')
             .where('u.status = %s', 'active')
             .and_where('o.total > %s', 100)
             .order_by('o.created_at', 'DESC')
             .limit(10)
             .build())
    print(query)
    
    print("\n=== 复杂查询 ===")
    query2 = (SQLQueryBuilder()
              .select('category', 'COUNT(*) as count', 'SUM(price) as total')
              .from_table('products')
              .where('status = %s', 'active')
              .group_by('category')
              .having('count > 5')
              .order_by('total', 'DESC')
              .build())
    print(query2)
    
    print("\n=== INSERT查询 ===")
    insert = (InsertBuilder()
              .into('users')
              .columns('name', 'email', 'status')
              .values('张三', 'zhang@example.com', 'active')
              .build())
    print(insert)
    
    print("\n=== UPDATE查询 ===")
    update = (UpdateBuilder()
              .table('users')
              .set(name='李四', status='inactive')
              .where('id = 1')
              .build())
    print(update)


if __name__ == "__main__":
    main()
