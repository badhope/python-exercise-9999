# -----------------------------
# 题目：实现简单的解释器模式。
# -----------------------------

from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

class Expression(ABC):
    @abstractmethod
    def interpret(self, context: Dict[str, Any]) -> Any:
        pass

class Context:
    def __init__(self, data: Dict[str, Any] = None):
        self.data = data or {}
        self.variables: Dict[str, Any] = {}
    
    def set(self, name: str, value: Any):
        self.variables[name] = value
    
    def get(self, name: str) -> Any:
        if name in self.variables:
            return self.variables[name]
        return self.data.get(name)

class NumberExpression(Expression):
    def __init__(self, value: float):
        self.value = value
    
    def interpret(self, context: Dict[str, Any]) -> float:
        return self.value

class VariableExpression(Expression):
    def __init__(self, name: str):
        self.name = name
    
    def interpret(self, context: Dict[str, Any]) -> Any:
        ctx = Context(context)
        return ctx.get(self.name)

class AddExpression(Expression):
    def __init__(self, left: Expression, right: Expression):
        self.left = left
        self.right = right
    
    def interpret(self, context: Dict[str, Any]) -> float:
        return self.left.interpret(context) + self.right.interpret(context)

class SubtractExpression(Expression):
    def __init__(self, left: Expression, right: Expression):
        self.left = left
        self.right = right
    
    def interpret(self, context: Dict[str, Any]) -> float:
        return self.left.interpret(context) - self.right.interpret(context)

class MultiplyExpression(Expression):
    def __init__(self, left: Expression, right: Expression):
        self.left = left
        self.right = right
    
    def interpret(self, context: Dict[str, Any]) -> float:
        return self.left.interpret(context) * self.right.interpret(context)

class DivideExpression(Expression):
    def __init__(self, left: Expression, right: Expression):
        self.left = left
        self.right = right
    
    def interpret(self, context: Dict[str, Any]) -> float:
        right_val = self.right.interpret(context)
        if right_val == 0:
            raise ValueError("除数不能为零")
        return self.left.interpret(context) / right_val

class EqualsExpression(Expression):
    def __init__(self, left: Expression, right: Expression):
        self.left = left
        self.right = right
    
    def interpret(self, context: Dict[str, Any]) -> bool:
        return self.left.interpret(context) == self.right.interpret(context)

class GreaterThanExpression(Expression):
    def __init__(self, left: Expression, right: Expression):
        self.left = left
        self.right = right
    
    def interpret(self, context: Dict[str, Any]) -> bool:
        return self.left.interpret(context) > self.right.interpret(context)

class AndExpression(Expression):
    def __init__(self, left: Expression, right: Expression):
        self.left = left
        self.right = right
    
    def interpret(self, context: Dict[str, Any]) -> bool:
        return self.left.interpret(context) and self.right.interpret(context)

class OrExpression(Expression):
    def __init__(self, left: Expression, right: Expression):
        self.left = left
        self.right = right
    
    def interpret(self, context: Dict[str, Any]) -> bool:
        return self.left.interpret(context) or self.right.interpret(context)

class ExpressionParser:
    def __init__(self):
        self.operators = {
            '+': (1, AddExpression),
            '-': (1, SubtractExpression),
            '*': (2, MultiplyExpression),
            '/': (2, DivideExpression)
        }
    
    def parse(self, expression: str) -> Expression:
        tokens = self._tokenize(expression)
        return self._build_ast(tokens)
    
    def _tokenize(self, expression: str) -> List[str]:
        tokens = []
        current = ''
        
        for char in expression:
            if char in '+-*/()':
                if current:
                    tokens.append(current)
                    current = ''
                tokens.append(char)
            elif char.isspace():
                if current:
                    tokens.append(current)
                    current = ''
            else:
                current += char
        
        if current:
            tokens.append(current)
        
        return tokens
    
    def _build_ast(self, tokens: List[str]) -> Expression:
        output = []
        operators = []
        
        for token in tokens:
            if token == '(':
                operators.append(token)
            elif token == ')':
                while operators and operators[-1] != '(':
                    self._apply_operator(output, operators.pop())
                operators.pop()
            elif token in self.operators:
                while (operators and operators[-1] != '(' and
                       self.operators.get(operators[-1], (0, None))[0] >= 
                       self.operators[token][0]):
                    self._apply_operator(output, operators.pop())
                operators.append(token)
            else:
                output.append(self._create_operand(token))
        
        while operators:
            self._apply_operator(output, operators.pop())
        
        return output[0] if output else NumberExpression(0)
    
    def _apply_operator(self, output: List[Expression], operator: str):
        right = output.pop()
        left = output.pop()
        expr_class = self.operators[operator][1]
        output.append(expr_class(left, right))
    
    def _create_operand(self, token: str) -> Expression:
        try:
            return NumberExpression(float(token))
        except ValueError:
            return VariableExpression(token)

def main():
    parser = ExpressionParser()
    
    print("=== 简单表达式 ===")
    expr = parser.parse("3 + 4 * 2")
    result = expr.interpret({})
    print(f"3 + 4 * 2 = {result}")
    
    print("\n=== 带括号表达式 ===")
    expr = parser.parse("(3 + 4) * 2")
    result = expr.interpret({})
    print(f"(3 + 4) * 2 = {result}")
    
    print("\n=== 带变量表达式 ===")
    expr = parser.parse("x * y + z")
    result = expr.interpret({'x': 2, 'y': 3, 'z': 4})
    print(f"x * y + z = {result} (x=2, y=3, z=4)")
    
    print("\n=== 复杂表达式 ===")
    expr = parser.parse("a + b * c - d / e")
    context = {'a': 10, 'b': 2, 'c': 3, 'd': 8, 'e': 4}
    result = expr.interpret(context)
    print(f"a + b * c - d / e = {result} (a=10, b=2, c=3, d=8, e=4)")
    
    print("\n=== 比较表达式 ===")
    expr = GreaterThanExpression(
        AddExpression(NumberExpression(3), NumberExpression(4)),
        NumberExpression(5)
    )
    result = expr.interpret({})
    print(f"3 + 4 > 5 = {result}")


if __name__ == "__main__":
    main()
