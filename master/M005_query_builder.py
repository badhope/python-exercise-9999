# -----------------------------
# 题目：实现简单的ORM查询构建器。
# 描述：支持链式调用构建SQL查询。
# -----------------------------

class QueryBuilder:
    def __init__(self, table):
        self.table = table
        self._select = ['*']
        self._where = []
        self._order = None
        self._limit = None
        self._offset = None
        self._params = []
    
    def select(self, *columns):
        self._select = columns if columns else ['*']
        return self
    
    def where(self, column, operator, value):
        self._where.append(f"{column} {operator} ?")
        self._params.append(value)
        return self
    
    def order_by(self, column, direction='ASC'):
        self._order = f"ORDER BY {column} {direction}"
        return self
    
    def limit(self, limit):
        self._limit = f"LIMIT {limit}"
        return self
    
    def offset(self, offset):
        self._offset = f"OFFSET {offset}"
        return self
    
    def to_sql(self):
        sql = f"SELECT {', '.join(self._select)} FROM {self.table}"
        
        if self._where:
            sql += f" WHERE {' AND '.join(self._where)}"
        
        if self._order:
            sql += f" {self._order}"
        
        if self._limit:
            sql += f" {self._limit}"
        
        if self._offset:
            sql += f" {self._offset}"
        
        return sql
    
    def get_params(self):
        return self._params

class Model:
    _table = None
    
    @classmethod
    def query(cls):
        return QueryBuilder(cls._table or cls.__name__.lower())
    
    @classmethod
    def all(cls):
        return cls.query().to_sql()
    
    @classmethod
    def find(cls, id):
        return cls.query().where('id', '=', id).to_sql()

class User(Model):
    _table = 'users'

def main():
    print("简单查询:")
    print(User.all())
    
    print("\n条件查询:")
    sql = User.query() \
        .select('id', 'name', 'email') \
        .where('age', '>', 18) \
        .where('status', '=', 'active') \
        .order_by('created_at', 'DESC') \
        .limit(10) \
        .to_sql()
    print(sql)


if __name__ == "__main__":
    main()
