# -----------------------------
# 题目：实现AST解析器。
# -----------------------------

import ast
from typing import Any, Dict, List

class ASTVisitor(ast.NodeVisitor):
    def __init__(self):
        self.variables: Dict[str, Any] = {}
        self.functions: List[str] = []
        self.classes: List[str] = []
        self.imports: List[str] = []
        self.calls: List[str] = []
    
    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom):
        module = node.module or ''
        for alias in node.names:
            self.imports.append(f"{module}.{alias.name}")
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.functions.append(node.name)
        self.generic_visit(node)
    
    def visit_ClassDef(self, node: ast.ClassDef):
        self.classes.append(node.name)
        self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Name):
            self.calls.append(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self.calls.append(node.func.attr)
        self.generic_visit(node)
    
    def visit_Assign(self, node: ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.variables[target.id] = None
        self.generic_visit(node)

class ExpressionEvaluator(ast.NodeVisitor):
    def __init__(self, context: Dict[str, Any] = None):
        self.context = context or {}
    
    def visit_Expression(self, node: ast.Expression):
        return self.visit(node.body)
    
    def visit_BinOp(self, node: ast.BinOp):
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        if isinstance(node.op, ast.Add):
            return left + right
        elif isinstance(node.op, ast.Sub):
            return left - right
        elif isinstance(node.op, ast.Mult):
            return left * right
        elif isinstance(node.op, ast.Div):
            return left / right
        elif isinstance(node.op, ast.FloorDiv):
            return left // right
        elif isinstance(node.op, ast.Mod):
            return left % right
        elif isinstance(node.op, ast.Pow):
            return left ** right
    
    def visit_UnaryOp(self, node: ast.UnaryOp):
        operand = self.visit(node.operand)
        
        if isinstance(node.op, ast.UAdd):
            return +operand
        elif isinstance(node.op, ast.USub):
            return -operand
        elif isinstance(node.op, ast.Not):
            return not operand
    
    def visit_Compare(self, node: ast.Compare):
        left = self.visit(node.left)
        
        for op, comparator in zip(node.ops, node.comparators):
            right = self.visit(comparator)
            
            if isinstance(op, ast.Eq):
                if not (left == right):
                    return False
            elif isinstance(op, ast.NotEq):
                if not (left != right):
                    return False
            elif isinstance(op, ast.Lt):
                if not (left < right):
                    return False
            elif isinstance(op, ast.LtE):
                if not (left <= right):
                    return False
            elif isinstance(op, ast.Gt):
                if not (left > right):
                    return False
            elif isinstance(op, ast.GtE):
                if not (left >= right):
                    return False
            
            left = right
        
        return True
    
    def visit_Name(self, node: ast.Name):
        return self.context.get(node.id)
    
    def visit_Constant(self, node: ast.Constant):
        return node.value
    
    def visit_List(self, node: ast.List):
        return [self.visit(elt) for elt in node.elts]
    
    def visit_Dict(self, node: ast.Dict):
        return {self.visit(k): self.visit(v) for k, v in zip(node.keys, node.values)}
    
    def visit_Subscript(self, node: ast.Subscript):
        value = self.visit(node.value)
        slice_val = self.visit(node.slice)
        return value[slice_val]
    
    def visit_Attribute(self, node: ast.Attribute):
        value = self.visit(node.value)
        return getattr(value, node.attr)

class CodeAnalyzer:
    def __init__(self, source: str):
        self.source = source
        self.tree = ast.parse(source)
    
    def analyze(self) -> Dict[str, Any]:
        visitor = ASTVisitor()
        visitor.visit(self.tree)
        
        return {
            'imports': visitor.imports,
            'functions': visitor.functions,
            'classes': visitor.classes,
            'variables': list(visitor.variables.keys()),
            'calls': visitor.calls
        }
    
    def get_complexity(self) -> int:
        complexity = 0
        
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity

def evaluate_expression(expr: str, context: Dict[str, Any] = None) -> Any:
    tree = ast.parse(expr, mode='eval')
    evaluator = ExpressionEvaluator(context)
    return evaluator.visit(tree)

def safe_eval(expr: str, context: Dict[str, Any] = None) -> Any:
    allowed_nodes = (
        ast.Expression, ast.BinOp, ast.UnaryOp, ast.Compare,
        ast.Constant, ast.Name, ast.List, ast.Dict, ast.Subscript,
        ast.Attribute, ast.Add, ast.Sub, ast.Mult, ast.Div,
        ast.FloorDiv, ast.Mod, ast.Pow, ast.Eq, ast.NotEq,
        ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Index
    )
    
    tree = ast.parse(expr, mode='eval')
    
    for node in ast.walk(tree):
        if not isinstance(node, allowed_nodes):
            raise ValueError(f"不允许的节点类型: {type(node).__name__}")
    
    return evaluate_expression(expr, context)

def main():
    print("=== 代码分析 ===")
    code = """
import os
from typing import List

def greet(name: str) -> str:
    return f"Hello, {name}!"

class Person:
    def __init__(self, name: str):
        self.name = name
    
    def say_hello(self):
        return greet(self.name)

x = 10
y = x + 5
print(greet("World"))
"""
    
    analyzer = CodeAnalyzer(code)
    result = analyzer.analyze()
    
    print(f"导入: {result['imports']}")
    print(f"函数: {result['functions']}")
    print(f"类: {result['classes']}")
    print(f"变量: {result['variables']}")
    print(f"调用: {result['calls']}")
    print(f"复杂度: {analyzer.get_complexity()}")
    
    print("\n=== 表达式求值 ===")
    expr = "2 + 3 * 4"
    result = evaluate_expression(expr)
    print(f"{expr} = {result}")
    
    expr = "x * y + z"
    result = evaluate_expression(expr, {'x': 2, 'y': 3, 'z': 4})
    print(f"{expr} (x=2, y=3, z=4) = {result}")
    
    print("\n=== 安全求值 ===")
    result = safe_eval("10 + 20 * 3")
    print(f"safe_eval('10 + 20 * 3') = {result}")


if __name__ == "__main__":
    main()
