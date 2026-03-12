# -----------------------------
# 题目：实现简单的表达式计算器。
# 描述：支持基本数学运算和括号。
# -----------------------------

import re

class ExpressionCalculator:
    def __init__(self):
        self.operators = {
            '+': lambda a, b: a + b,
            '-': lambda a, b: a - b,
            '*': lambda a, b: a * b,
            '/': lambda a, b: a / b if b != 0 else float('inf'),
            '%': lambda a, b: a % b if b != 0 else float('nan'),
            '^': lambda a, b: a ** b
        }
        self.precedence = {'+': 1, '-': 1, '*': 2, '/': 2, '%': 2, '^': 3}
    
    def calculate(self, expression):
        expression = expression.replace(' ', '')
        tokens = self._tokenize(expression)
        postfix = self._to_postfix(tokens)
        return self._evaluate_postfix(postfix)
    
    def _tokenize(self, expression):
        tokens = []
        i = 0
        while i < len(expression):
            if expression[i].isdigit() or expression[i] == '.':
                j = i
                while j < len(expression) and (expression[j].isdigit() or expression[j] == '.'):
                    j += 1
                tokens.append(float(expression[i:j]))
                i = j
            elif expression[i] in '+-*/%^()':
                tokens.append(expression[i])
                i += 1
            else:
                i += 1
        return tokens
    
    def _to_postfix(self, tokens):
        output = []
        stack = []
        
        for token in tokens:
            if isinstance(token, float):
                output.append(token)
            elif token == '(':
                stack.append(token)
            elif token == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                stack.pop()
            else:
                while (stack and stack[-1] != '(' and
                       self.precedence.get(stack[-1], 0) >= self.precedence.get(token, 0)):
                    output.append(stack.pop())
                stack.append(token)
        
        while stack:
            output.append(stack.pop())
        
        return output
    
    def _evaluate_postfix(self, postfix):
        stack = []
        
        for token in postfix:
            if isinstance(token, float):
                stack.append(token)
            elif token in self.operators:
                b = stack.pop()
                a = stack.pop()
                result = self.operators[token](a, b)
                stack.append(result)
        
        return stack[0] if stack else 0
    
    def validate(self, expression):
        try:
            self.calculate(expression)
            return True, "表达式有效"
        except Exception as e:
            return False, f"表达式无效: {e}"

def main():
    calc = ExpressionCalculator()
    
    expressions = [
        "2 + 3 * 4",
        "(2 + 3) * 4",
        "10 / 2 - 3",
        "2 ^ 3 + 1",
        "10 % 3"
    ]
    
    print("表达式计算:")
    for expr in expressions:
        result = calc.calculate(expr)
        print(f"  {expr} = {result}")


if __name__ == "__main__":
    main()
