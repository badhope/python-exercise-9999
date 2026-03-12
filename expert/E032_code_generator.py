# -----------------------------
# 题目：实现代码生成器。
# -----------------------------

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from string import Template

@dataclass
class Field:
    name: str
    type: str
    default: Any = None
    nullable: bool = True

@dataclass
class Method:
    name: str
    params: List[tuple]
    return_type: str
    body: str

class ClassGenerator:
    def __init__(self, class_name: str, base_class: str = None):
        self.class_name = class_name
        self.base_class = base_class
        self.fields: List[Field] = []
        self.methods: List[Method] = []
        self.imports: List[str] = []
    
    def add_field(self, name: str, type: str, default: Any = None, nullable: bool = True):
        self.fields.append(Field(name, type, default, nullable))
        return self
    
    def add_method(self, name: str, params: List[tuple], return_type: str, body: str):
        self.methods.append(Method(name, params, return_type, body))
        return self
    
    def add_import(self, module: str):
        self.imports.append(module)
        return self
    
    def generate(self) -> str:
        lines = []
        
        if self.imports:
            for imp in self.imports:
                lines.append(f"from {imp} import *")
            lines.append("")
        
        class_def = f"class {self.class_name}"
        if self.base_class:
            class_def += f"({self.base_class})"
        lines.append(class_def)
        
        lines.append(self._generate_init())
        
        for method in self.methods:
            lines.append(self._generate_method(method))
        
        return "\n".join(lines)
    
    def _generate_init(self) -> str:
        params = ["self"]
        assignments = []
        
        for field in self.fields:
            if field.default is not None:
                params.append(f"{field.name}={repr(field.default)}")
            elif field.nullable:
                params.append(f"{field.name}=None")
            else:
                params.append(field.name)
            
            assignments.append(f"        self.{field.name} = {field.name}")
        
        lines = [f"    def __init__({', '.join(params)}):"]
        lines.extend(assignments)
        lines.append("")
        
        return "\n".join(lines)
    
    def _generate_method(self, method: Method) -> str:
        params = ["self"] + [f"{p[0]}: {p[1]}" for p in method.params]
        
        lines = [f"    def {method.name}({', '.join(params)}) -> {method.return_type}:"]
        
        for line in method.body.split("\n"):
            lines.append(f"        {line}")
        
        lines.append("")
        
        return "\n".join(lines)

class DataClassGenerator:
    @staticmethod
    def generate(class_name: str, fields: Dict[str, str]) -> str:
        lines = ["from dataclasses import dataclass", ""]
        lines.append("@dataclass")
        lines.append(f"class {class_name}:")
        
        for name, type_ in fields.items():
            lines.append(f"    {name}: {type_}")
        
        return "\n".join(lines)

class PydanticGenerator:
    @staticmethod
    def generate(class_name: str, fields: Dict[str, tuple]) -> str:
        lines = ["from pydantic import BaseModel", ""]
        lines.append(f"class {class_name}(BaseModel):")
        
        for name, (type_, *constraints) in fields.items():
            if constraints:
                constraints_str = ", ".join(str(c) for c in constraints)
                lines.append(f"    {name}: {type_} = Field({constraints_str})")
            else:
                lines.append(f"    {name}: {type_}")
        
        return "\n".join(lines)

class SQLGenerator:
    @staticmethod
    def create_table(table_name: str, columns: Dict[str, str], primary_key: str = None) -> str:
        col_defs = []
        
        for name, type_ in columns.items():
            col_def = f"    {name} {type_}"
            if name == primary_key:
                col_def += " PRIMARY KEY"
            col_defs.append(col_def)
        
        return f"CREATE TABLE {table_name} (\n" + ",\n".join(col_defs) + "\n);"
    
    @staticmethod
    def insert(table_name: str, columns: List[str]) -> str:
        cols = ", ".join(columns)
        placeholders = ", ".join(["%s"] * len(columns))
        return f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders});"
    
    @staticmethod
    def select(table_name: str, columns: List[str] = None, where: str = None) -> str:
        cols = ", ".join(columns) if columns else "*"
        sql = f"SELECT {cols} FROM {table_name}"
        
        if where:
            sql += f" WHERE {where}"
        
        return sql + ";"

class APIGenerator:
    @staticmethod
    def generate_endpoint(method: str, path: str, handler_name: str, params: List[tuple] = None) -> str:
        decorator = f"@app.{method.lower()}('{path}')"
        
        params_str = ""
        if params:
            params_str = ", ".join(f"{p[0]}: {p[1]}" for p in params)
        
        return f"""{decorator}
async def {handler_name}({params_str}):
    pass
"""

class TestGenerator:
    @staticmethod
    def generate_unit_test(class_name: str, method_name: str) -> str:
        return f"""import unittest

class Test{class_name}(unittest.TestCase):
    def setUp(self):
        pass
    
    def test_{method_name}(self):
        pass
    
    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
"""

def main():
    print("=== 类生成器 ===")
    gen = (ClassGenerator("User", "BaseModel")
           .add_import("typing")
           .add_field("id", "int", nullable=False)
           .add_field("name", "str", nullable=False)
           .add_field("email", "str")
           .add_method("greet", [], "str", 'return f"Hello, {self.name}"'))
    
    print(gen.generate())
    
    print("\n=== DataClass生成器 ===")
    code = DataClassGenerator.generate("Person", {
        "name": "str",
        "age": "int",
        "email": "Optional[str]"
    })
    print(code)
    
    print("\n=== SQL生成器 ===")
    sql = SQLGenerator.create_table("users", {
        "id": "INTEGER",
        "name": "VARCHAR(100)",
        "email": "VARCHAR(255)"
    }, primary_key="id")
    print(sql)
    
    print("\n=== API生成器 ===")
    api = APIGenerator.generate_endpoint("GET", "/users/{user_id}", "get_user", [("user_id", "int")])
    print(api)
    
    print("\n=== 测试生成器 ===")
    test = TestGenerator.generate_unit_test("Calculator", "add")
    print(test)


if __name__ == "__main__":
    main()
