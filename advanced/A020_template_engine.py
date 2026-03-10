# -----------------------------
# 题目：实现简易模板引擎。
# -----------------------------

import re

class TemplateEngine:
    def __init__(self, template):
        self.template = template
    
    def render(self, context):
        result = self.template
        for key, value in context.items():
            pattern = r'\{\{\s*' + re.escape(key) + r'\s*\}\}'
            result = re.sub(pattern, str(value), result)
        return result

def main():
    template = """
    <html>
    <body>
        <h1>欢迎, {{ username }}</h1>
        <p>您的积分: {{ points }}</p>
    </body>
    </html>
    """
    engine = TemplateEngine(template)
    context = {"username": "张三", "points": 1500}
    print(engine.render(context))


if __name__ == "__main__":
    main()
