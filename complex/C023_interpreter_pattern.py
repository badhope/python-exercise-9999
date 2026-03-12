# -----------------------------
# 题目：解释器模式实现简单数学表达式计算。
# -----------------------------

class Expression:
    def interpret(self, context):
        pass

class Number(Expression):
    def __init__(self, number):
        self.number = number
    
    def interpret(self, context):
        return self.number

class Variable(Expression):
    def __init__(self, name):
        self.name = name
    
    def interpret(self, context):
        return context.get(self.name, 0)

class Add(Expression):
    def __init__(self, left, right):
        self.left = left
        self.right = right
    
    def interpret(self, context):
        return self.left.interpret(context) + self.right.interpret(context)

class Subtract(Expression):
    def __init__(self, left, right):
        self.left = left
        self.right = right
    
    def interpret(self, context):
        return self.left.interpret(context) - self.right.interpret(context)

class Multiply(Expression):
    def __init__(self, left, right):
        self.left = left
        self.right = right
    
    def interpret(self, context):
        return self.left.interpret(context) * self.right.interpret(context)

class Divide(Expression):
    def __init__(self, left, right):
        self.left = left
        self.right = right
    
    def interpret(self, context):
        right_val = self.right.interpret(context)
        if right_val == 0:
            raise ValueError("除数不能为零")
        return self.left.interpret(context) / right_val

class Parser:
    def __init__(self, expression):
        self.tokens = expression.replace('+', ' + ').replace('-', ' - ').replace('*', ' * ').replace('/', ' / ').replace('(', ' ( ').replace(')', ' ) ').split()
        self.pos = 0
    
    def parse(self):
        return self._parse_expression()
    
    def _parse_expression(self):
        left = self._parse_term()
        while self.pos < len(self.tokens) and self.tokens[self.pos] in ['+', '-']:
            op = self.tokens[self.pos]
            self.pos += 1
            right = self._parse_term()
            if op == '+':
                left = Add(left, right)
            else:
                left = Subtract(left, right)
        return left
    
    def _parse_term(self):
        left = self._parse_factor()
        while self.pos < len(self.tokens) and self.tokens[self.pos] in ['*', '/']:
            op = self.tokens[self.pos]
            self.pos += 1
            right = self._parse_factor()
            if op == '*':
                left = Multiply(left, right)
            else:
                left = Divide(left, right)
        return left
    
    def _parse_factor(self):
        if self.tokens[self.pos] == '(':
            self.pos += 1
            expr = self._parse_expression()
            self.pos += 1
            return expr
        token = self.tokens[self.pos]
        self.pos += 1
        if token.isdigit() or (token[0] == '-' and token[1:].isdigit()):
            return Number(int(token))
        return Variable(token)

def main():
    context = {'x': 10, 'y': 5}
    
    expressions = [
        "3 + 4",
        "x + y",
        "x * y + 2",
        "(x + y) * 2",
        "x - y / 5"
    ]
    
    for expr in expressions:
        parser = Parser(expr)
        ast = parser.parse()
        result = ast.interpret(context)
        print(f"{expr} = {result}")


if __name__ == "__main__":
    main()
