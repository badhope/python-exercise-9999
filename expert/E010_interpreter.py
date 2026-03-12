# -----------------------------
# 题目：实现简单的解释器模式。
# 描述：解析和执行简单表达式。
# -----------------------------

class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
    
    def get_next_token(self):
        while self.pos < len(self.text):
            char = self.text[self.pos]
            if char.isspace():
                self.pos += 1
                continue
            if char.isdigit():
                return self._read_number()
            if char in '+-*/()':
                self.pos += 1
                return Token(char, char)
        return Token('EOF', None)
    
    def _read_number(self):
        result = ''
        while self.pos < len(self.text) and self.text[self.pos].isdigit():
            result += self.text[self.pos]
            self.pos += 1
        return Token('NUMBER', int(result))

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
    
    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            raise SyntaxError(f"期望 {token_type}, 得到 {self.current_token.type}")
    
    def factor(self):
        token = self.current_token
        if token.type == 'NUMBER':
            self.eat('NUMBER')
            return token.value
        elif token.type == '(':
            self.eat('(')
            result = self.expr()
            self.eat(')')
            return result
    
    def term(self):
        result = self.factor()
        while self.current_token.type in '*/':
            op = self.current_token.type
            self.eat(op)
            if op == '*':
                result *= self.factor()
            else:
                result //= self.factor()
        return result
    
    def expr(self):
        result = self.term()
        while self.current_token.type in '+-':
            op = self.current_token.type
            self.eat(op)
            if op == '+':
                result += self.term()
            else:
                result -= self.term()
        return result

def main():
    expressions = ["3 + 5", "10 - 3 * 2", "(2 + 3) * 4"]
    for expr in expressions:
        lexer = Lexer(expr)
        parser = Parser(lexer)
        result = parser.expr()
        print(f"{expr} = {result}")


if __name__ == "__main__":
    main()
