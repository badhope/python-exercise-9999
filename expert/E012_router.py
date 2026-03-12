# -----------------------------
# 题目：实现简单的路由系统。
# 描述：支持动态路由和参数提取。
# -----------------------------

import re

class Route:
    def __init__(self, pattern, handler):
        self.pattern = pattern
        self.handler = handler
        self.param_names = []
        self.regex = self._compile(pattern)
    
    def _compile(self, pattern):
        regex_parts = ['^']
        parts = pattern.split('/')
        for part in parts:
            if part.startswith('<') and part.endswith('>'):
                param_name = part[1:-1]
                self.param_names.append(param_name)
                regex_parts.append(r'([^/]+)')
            else:
                regex_parts.append(re.escape(part))
        regex_parts.append('$')
        return re.compile('/'.join(regex_parts))
    
    def match(self, path):
        match = self.regex.match(path)
        if match:
            params = dict(zip(self.param_names, match.groups()))
            return params
        return None

class Router:
    def __init__(self):
        self.routes = []
    
    def add_route(self, pattern, handler):
        self.routes.append(Route(pattern, handler))
    
    def route(self, pattern):
        def decorator(handler):
            self.add_route(pattern, handler)
            return handler
        return decorator
    
    def dispatch(self, path):
        for route in self.routes:
            params = route.match(path)
            if params is not None:
                return route.handler, params
        return None, None

def main():
    router = Router()
    
    @router.route('/')
    def index(params):
        return "首页"
    
    @router.route('/users/<user_id>')
    def user_detail(params):
        return f"用户详情: {params['user_id']}"
    
    @router.route('/posts/<post_id>/comments/<comment_id>')
    def comment(params):
        return f"评论: post={params['post_id']}, comment={params['comment_id']}"
    
    paths = ['/', '/users/123', '/posts/456/comments/789']
    for path in paths:
        handler, params = router.dispatch(path)
        if handler:
            print(f"{path} -> {handler(params)}")


if __name__ == "__main__":
    main()
