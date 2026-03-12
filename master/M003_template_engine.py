# -----------------------------
# 题目：实现简单的模板引擎。
# 描述：支持变量、循环、条件渲染。
# -----------------------------

import re

class TemplateEngine:
    def __init__(self):
        self.filters = {
            'upper': str.upper,
            'lower': str.lower,
            'title': str.title,
        }
    
    def render(self, template, context):
        result = template
        result = self._render_for(result, context)
        result = self._render_if(result, context)
        result = self._render_variables(result, context)
        return result
    
    def _render_variables(self, template, context):
        pattern = r'\{\{\s*(\w+)(?:\|(\w+))?\s*\}\}'
        
        def replace(match):
            var_name = match.group(1)
            filter_name = match.group(2)
            value = context.get(var_name, '')
            if filter_name and filter_name in self.filters:
                value = self.filters[filter_name](str(value))
            return str(value)
        
        return re.sub(pattern, replace, template)
    
    def _render_for(self, template, context):
        pattern = r'\{%\s*for\s+(\w+)\s+in\s+(\w+)\s*%\}(.*?)\{%\s*endfor\s*%\}'
        
        def replace(match):
            item_name = match.group(1)
            list_name = match.group(2)
            body = match.group(3)
            items = context.get(list_name, [])
            result = []
            for item in items:
                item_context = context.copy()
                item_context[item_name] = item
                result.append(self._render_variables(body, item_context))
            return ''.join(result)
        
        return re.sub(pattern, replace, template, flags=re.DOTALL)
    
    def _render_if(self, template, context):
        pattern = r'\{%\s*if\s+(\w+)\s*%\}(.*?)\{%\s*endif\s*%\}'
        
        def replace(match):
            var_name = match.group(1)
            body = match.group(2)
            if context.get(var_name):
                return body
            return ''
        
        return re.sub(pattern, replace, template, flags=re.DOTALL)

def main():
    engine = TemplateEngine()
    template = """
    <h1>{{ title }}</h1>
    <ul>
    {% for item in items %}
        <li>{{ item }}</li>
    {% endfor %}
    </ul>
    {% if show_footer %}
    <footer>Footer</footer>
    {% endif %}
    """
    context = {
        'title': 'My List',
        'items': ['Apple', 'Banana', 'Cherry'],
        'show_footer': True
    }
    print(engine.render(template, context))


if __name__ == "__main__":
    main()
