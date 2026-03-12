# -----------------------------
# 题目：实现模板引擎。
# 描述：支持变量插值、条件渲染、循环渲染。
# -----------------------------

import re
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass

@dataclass
class Token:
    type: str
    value: str
    line: int = 0

class Lexer:
    def __init__(self, template: str):
        self.template = template
        self.pos = 0
        self.line = 1
    
    def tokenize(self) -> List[Token]:
        tokens = []
        pattern = r'(\{\{.*?\}\}|\{%.*?%\}|\{#.*?#\})'
        
        last_end = 0
        for match in re.finditer(pattern, self.template):
            if match.start() > last_end:
                text = self.template[last_end:match.start()]
                if text:
                    tokens.append(Token('TEXT', text, self.line))
                    self.line += text.count('\n')
            
            token_str = match.group(1)
            
            if token_str.startswith('{{'):
                content = token_str[2:-2].strip()
                tokens.append(Token('VAR', content, self.line))
            elif token_str.startswith('{%'):
                content = token_str[2:-2].strip()
                tokens.append(Token('TAG', content, self.line))
            elif token_str.startswith('{#'):
                pass
            
            last_end = match.end()
        
        if last_end < len(self.template):
            text = self.template[last_end:]
            if text:
                tokens.append(Token('TEXT', text, self.line))
        
        return tokens

class Node:
    pass

@dataclass
class TextNode(Node):
    text: str

@dataclass
class VarNode(Node):
    expression: str

@dataclass
class IfNode(Node):
    condition: str
    true_body: List[Node]
    false_body: List[Node]

@dataclass
class ForNode(Node):
    var_name: str
    iterable: str
    body: List[Node]

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
    
    def parse(self) -> List[Node]:
        return self._parse_body()
    
    def _parse_body(self, end_tags: List[str] = None) -> List[Node]:
        nodes = []
        end_tags = end_tags or []
        
        while self.pos < len(self.tokens):
            token = self.tokens[self.pos]
            
            if token.type == 'TAG':
                tag_parts = token.value.split()
                tag_name = tag_parts[0] if tag_parts else ''
                
                if tag_name in end_tags:
                    break
                elif tag_name == 'if':
                    nodes.append(self._parse_if())
                elif tag_name == 'for':
                    nodes.append(self._parse_for())
                elif tag_name in ('endif', 'endfor', 'else', 'elif'):
                    break
                else:
                    self.pos += 1
            elif token.type == 'VAR':
                nodes.append(VarNode(token.value))
                self.pos += 1
            elif token.type == 'TEXT':
                nodes.append(TextNode(token.value))
                self.pos += 1
            else:
                self.pos += 1
        
        return nodes
    
    def _parse_if(self) -> IfNode:
        token = self.tokens[self.pos]
        condition = token.value[3:].strip()
        self.pos += 1
        
        true_body = self._parse_body(['else', 'elif', 'endif'])
        false_body = []
        
        if self.pos < len(self.tokens):
            next_token = self.tokens[self.pos]
            if next_token.type == 'TAG':
                tag_parts = next_token.value.split()
                tag_name = tag_parts[0] if tag_parts else ''
                
                if tag_name == 'else':
                    self.pos += 1
                    false_body = self._parse_body(['endif'])
                    self.pos += 1
                elif tag_name == 'endif':
                    self.pos += 1
        
        return IfNode(condition, true_body, false_body)
    
    def _parse_for(self) -> ForNode:
        token = self.tokens[self.pos]
        content = token.value[4:].strip()
        
        parts = content.split(' in ')
        var_name = parts[0].strip()
        iterable = parts[1].strip() if len(parts) > 1 else ''
        
        self.pos += 1
        
        body = self._parse_body(['endfor'])
        
        if self.pos < len(self.tokens):
            next_token = self.tokens[self.pos]
            if next_token.type == 'TAG' and next_token.value == 'endfor':
                self.pos += 1
        
        return ForNode(var_name, iterable, body)

class Context:
    def __init__(self, data: Dict[str, Any] = None, parent: 'Context' = None):
        self.data = data or {}
        self.parent = parent
    
    def get(self, key: str, default: Any = None) -> Any:
        if key in self.data:
            return self.data[key]
        if self.parent:
            return self.parent.get(key, default)
        return default
    
    def set(self, key: str, value: Any):
        self.data[key] = value
    
    def child(self, data: Dict[str, Any] = None) -> 'Context':
        return Context(data, self)

class Renderer:
    def __init__(self):
        self.filters: Dict[str, Callable] = {
            'upper': lambda x: str(x).upper(),
            'lower': lambda x: str(x).lower(),
            'capitalize': lambda x: str(x).capitalize(),
            'length': lambda x: len(x) if hasattr(x, '__len__') else 0,
            'default': lambda x, d='': x if x else d,
        }
    
    def render(self, nodes: List[Node], context: Context) -> str:
        result = []
        
        for node in nodes:
            if isinstance(node, TextNode):
                result.append(node.text)
            elif isinstance(node, VarNode):
                result.append(str(self._eval_var(node.expression, context)))
            elif isinstance(node, IfNode):
                result.append(self._render_if(node, context))
            elif isinstance(node, ForNode):
                result.append(self._render_for(node, context))
        
        return ''.join(result)
    
    def _eval_var(self, expression: str, context: Context) -> Any:
        parts = expression.split('|')
        var_expr = parts[0].strip()
        
        value = self._eval_expression(var_expr, context)
        
        for filter_expr in parts[1:]:
            filter_expr = filter_expr.strip()
            
            if '(' in filter_expr:
                filter_name = filter_expr[:filter_expr.index('(')]
                args_str = filter_expr[filter_expr.index('(')+1:-1]
                args = [self._eval_expression(a.strip(), context) for a in args_str.split(',')] if args_str else []
                
                filter_func = self.filters.get(filter_name)
                if filter_func:
                    value = filter_func(value, *args)
            else:
                filter_func = self.filters.get(filter_expr)
                if filter_func:
                    value = filter_func(value)
        
        return value
    
    def _eval_expression(self, expr: str, context: Context) -> Any:
        expr = expr.strip()
        
        if expr.isdigit():
            return int(expr)
        if expr.startswith('"') or expr.startswith("'"):
            return expr[1:-1]
        if expr == 'True' or expr == 'true':
            return True
        if expr == 'False' or expr == 'false':
            return False
        if expr == 'None' or expr == 'null':
            return None
        
        parts = expr.split('.')
        value = context.get(parts[0])
        
        for part in parts[1:]:
            if value is None:
                return None
            if isinstance(value, dict):
                value = value.get(part)
            else:
                value = getattr(value, part, None)
        
        return value
    
    def _render_if(self, node: IfNode, context: Context) -> str:
        condition_value = self._eval_expression(node.condition, context)
        
        if condition_value:
            return self.render(node.true_body, context)
        else:
            return self.render(node.false_body, context)
    
    def _render_for(self, node: ForNode, context: Context) -> str:
        iterable = self._eval_expression(node.iterable, context)
        
        if not iterable:
            return ''
        
        result = []
        for i, item in enumerate(iterable):
            child_context = context.child({
                node.var_name: item,
                'loop': {
                    'index': i + 1,
                    'index0': i,
                    'first': i == 0,
                    'last': i == len(iterable) - 1,
                    'length': len(iterable)
                }
            })
            result.append(self.render(node.body, child_context))
        
        return ''.join(result)

class TemplateEngine:
    def __init__(self):
        self.renderer = Renderer()
        self._cache: Dict[str, List[Node]] = {}
    
    def render(self, template: str, context: Dict[str, Any]) -> str:
        if template not in self._cache:
            lexer = Lexer(template)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            self._cache[template] = parser.parse()
        
        nodes = self._cache[template]
        ctx = Context(context)
        
        return self.renderer.render(nodes, ctx)
    
    def render_file(self, filepath: str, context: Dict[str, Any]) -> str:
        with open(filepath, 'r', encoding='utf-8') as f:
            template = f.read()
        return self.render(template, context)
    
    def add_filter(self, name: str, func: Callable):
        self.renderer.filters[name] = func

def main():
    engine = TemplateEngine()
    
    template = """
<html>
<head><title>{{ title }}</title></head>
<body>
    <h1>{{ title }}</h1>
    
    {% if user %}
    <p>欢迎, {{ user.name }}!</p>
    {% else %}
    <p>请登录</p>
    {% endif %}
    
    <ul>
    {% for item in items %}
        <li>{{ loop.index }}. {{ item.name }} - {{ item.price | upper }}</li>
    {% endfor %}
    </ul>
</body>
</html>
"""
    
    context = {
        'title': '商品列表',
        'user': {'name': '张三'},
        'items': [
            {'name': '苹果', 'price': '10元'},
            {'name': '香蕉', 'price': '8元'},
            {'name': '橙子', 'price': '12元'},
        ]
    }
    
    result = engine.render(template, context)
    print(result)

if __name__ == "__main__":
    main()
