# -----------------------------
# 题目：实现简单的模板引擎。
# -----------------------------

import re
from typing import Dict, Any, List, Callable

class TemplateEngine:
    def __init__(self):
        self.filters: Dict[str, Callable] = {}
        self.tags: Dict[str, Callable] = {}
        self._register_builtin()
    
    def _register_builtin(self):
        self.filters['upper'] = lambda x: str(x).upper()
        self.filters['lower'] = lambda x: str(x).lower()
        self.filters['capitalize'] = lambda x: str(x).capitalize()
        self.filters['reverse'] = lambda x: str(x)[::-1]
        self.filters['length'] = lambda x: len(x)
        self.filters['default'] = lambda x, default='': x if x else default
        self.filters['join'] = lambda x, sep=', ': sep.join(str(i) for i in x)
        self.filters['first'] = lambda x: x[0] if x else ''
        self.filters['last'] = lambda x: x[-1] if x else ''
    
    def register_filter(self, name: str, func: Callable):
        self.filters[name] = func
    
    def register_tag(self, name: str, func: Callable):
        self.tags[name] = func
    
    def render(self, template: str, context: Dict[str, Any]) -> str:
        result = self._process_for(template, context)
        result = self._process_if(result, context)
        result = self._process_variables(result, context)
        return result
    
    def _process_variables(self, template: str, context: Dict[str, Any]) -> str:
        pattern = r'\{\{\s*([^}]+)\s*\}\}'
        
        def replace(match):
            expr = match.group(1).strip()
            return self._evaluate_expression(expr, context)
        
        return re.sub(pattern, replace, template)
    
    def _evaluate_expression(self, expr: str, context: Dict[str, Any]) -> str:
        parts = expr.split('|')
        var_expr = parts[0].strip()
        
        value = self._get_variable(var_expr, context)
        
        for filter_expr in parts[1:]:
            filter_expr = filter_expr.strip()
            if ':' in filter_expr:
                filter_name, args = filter_expr.split(':', 1)
                filter_name = filter_name.strip()
                args = args.strip().strip('"\'')
                if filter_name in self.filters:
                    value = self.filters[filter_name](value, args)
            else:
                filter_name = filter_expr.strip()
                if filter_name in self.filters:
                    value = self.filters[filter_name](value)
        
        return str(value) if value is not None else ''
    
    def _get_variable(self, expr: str, context: Dict[str, Any]) -> Any:
        parts = expr.split('.')
        value = context
        
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            elif hasattr(value, part):
                value = getattr(value, part)
            else:
                return None
            
            if value is None:
                return None
        
        return value
    
    def _process_for(self, template: str, context: Dict[str, Any]) -> str:
        pattern = r'\{%\s*for\s+(\w+)\s+in\s+(\w+)\s*%\}(.*?)\{%\s*endfor\s*%\}'
        
        def replace(match):
            var_name = match.group(1)
            list_name = match.group(2)
            body = match.group(3)
            
            items = context.get(list_name, [])
            results = []
            
            for i, item in enumerate(items):
                item_context = context.copy()
                item_context[var_name] = item
                item_context['loop'] = {
                    'index': i,
                    'index1': i + 1,
                    'first': i == 0,
                    'last': i == len(items) - 1,
                    'length': len(items)
                }
                result = self._process_if(body, item_context)
                result = self._process_variables(result, item_context)
                results.append(result)
            
            return ''.join(results)
        
        return re.sub(pattern, replace, template, flags=re.DOTALL)
    
    def _process_if(self, template: str, context: Dict[str, Any]) -> str:
        pattern = r'\{%\s*if\s+([^%]+)\s*%\}(.*?)(?:\{%\s*else\s*%\}(.*?))?\{%\s*endif\s*%\}'
        
        def replace(match):
            condition = match.group(1).strip()
            if_body = match.group(2)
            else_body = match.group(3) or ''
            
            if self._evaluate_condition(condition, context):
                return if_body
            return else_body
        
        return re.sub(pattern, replace, template, flags=re.DOTALL)
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        if '==' in condition:
            left, right = condition.split('==')
            left_val = self._get_variable(left.strip(), context)
            right_val = right.strip().strip('"\'')
            return str(left_val) == right_val
        
        if '!=' in condition:
            left, right = condition.split('!=')
            left_val = self._get_variable(left.strip(), context)
            right_val = right.strip().strip('"\'')
            return str(left_val) != right_val
        
        value = self._get_variable(condition, context)
        return bool(value)

class TemplateLoader:
    def __init__(self, template_dir: str = 'templates'):
        self.template_dir = template_dir
        self.cache: Dict[str, str] = {}
    
    def load(self, name: str) -> str:
        if name in self.cache:
            return self.cache[name]
        
        import os
        filepath = os.path.join(self.template_dir, name)
        with open(filepath, 'r', encoding='utf-8') as f:
            template = f.read()
        
        self.cache[name] = template
        return template

def main():
    engine = TemplateEngine()
    
    print("=== 变量替换 ===")
    template = "你好，{{ name }}！欢迎来到{{ city }}。"
    result = engine.render(template, {'name': '张三', 'city': '北京'})
    print(result)
    
    print("\n=== 过滤器 ===")
    template = "姓名: {{ name|upper }}，城市: {{ city|lower }}"
    result = engine.render(template, {'name': 'Zhang San', 'city': 'BEIJING'})
    print(result)
    
    print("\n=== 循环 ===")
    template = """
用户列表：
{% for user in users %}
{{ loop.index1 }}. {{ user.name }} ({{ user.email }})
{% endfor %}
"""
    result = engine.render(template, {
        'users': [
            {'name': '张三', 'email': 'zhang@example.com'},
            {'name': '李四', 'email': 'li@example.com'},
            {'name': '王五', 'email': 'wang@example.com'}
        ]
    })
    print(result)
    
    print("\n=== 条件判断 ===")
    template = """
{% if logged_in %}
欢迎回来，{{ username }}！
{% else %}
请先登录。
{% endif %}
"""
    print("已登录:")
    print(engine.render(template, {'logged_in': True, 'username': '张三'}))
    print("未登录:")
    print(engine.render(template, {'logged_in': False}))


if __name__ == "__main__":
    main()
