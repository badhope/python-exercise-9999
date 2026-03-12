# -----------------------------
# 题目：实现模板引擎。
# -----------------------------

import re
from html import escape

class TemplateEngine:
    def __init__(self):
        self.globals = {}
    
    def render(self, template, **context):
        result = template
        
        result = re.sub(r'\{\{%\s*for\s+(\w+)\s+in\s+(\w+)\s*%\}\}', 
                       self._handle_for, result)
        
        result = re.sub(r'\{\{%\s*if\s+(.+?)\s*%\}\}', 
                       self._handle_if, result)
        
        result = re.sub(r'\{\{\s*(.+?)\s*\}\}', 
                       lambda m: self._handle_var(m.group(1), context), result)
        
        result = re.sub(r'\{\{%\s*endif\s*%\}\}', '', result)
        result = re.sub(r'\{\{%\s*endfor\s*%\}\}', '', result)
        
        return result
    
    def _handle_for(self, match):
        var, iterable = match.groups()
        return f'__FOR_{var}_{iterable}__'
    
    def _handle_if(self, match):
        condition = match.group(1).strip()
        return f'__IF_{condition}__'
    
    def _handle_var(self, var, context):
        var = var.strip()
        if '.' in var:
            parts = var.split('.')
            value = context
            for p in parts:
                value = getattr(value, p, {})
            return str(value) if value else ''
        
        if var in self.globals:
            return str(self.globals[var])
        if var in context:
            val = context[var]
            if isinstance(val, (list, tuple)):
                return '|'.join(str(x) for x in val)
            return str(val)
        return ''

if __name__ == "__main__":
    engine = TemplateEngine()
    
    template = """
    <h1>{{ title }}</h1>
    <ul>
    {% for item in items %}
    <li>{{ item }}</li>
    {% endfor %}
    </ul>
    """
    
    result = engine.render(template, title="My List", items=["A", "B", "C"])
    print(result)
