# -----------------------------
# 题目：实现简单的JSON格式化工具。
# 描述：格式化JSON字符串，支持压缩和美化。
# -----------------------------

import json

class JSONFormatter:
    def __init__(self):
        self.indent = 2
    
    def beautify(self, json_str, indent=2):
        try:
            data = json.loads(json_str)
            return json.dumps(data, indent=indent, ensure_ascii=False)
        except json.JSONDecodeError as e:
            return f"JSON解析错误: {e}"
    
    def minify(self, json_str):
        try:
            data = json.loads(json_str)
            return json.dumps(data, separators=(',', ':'), ensure_ascii=False)
        except json.JSONDecodeError as e:
            return f"JSON解析错误: {e}"
    
    def validate(self, json_str):
        try:
            json.loads(json_str)
            return True, "JSON格式正确"
        except json.JSONDecodeError as e:
            return False, f"JSON格式错误: {e}"
    
    def sort_keys(self, json_str, indent=2):
        try:
            data = json.loads(json_str)
            return json.dumps(data, indent=indent, sort_keys=True, ensure_ascii=False)
        except json.JSONDecodeError as e:
            return f"JSON解析错误: {e}"
    
    def get_type(self, json_str):
        try:
            data = json.loads(json_str)
            return type(data).__name__
        except json.JSONDecodeError:
            return "invalid"
    
    def get_depth(self, json_str):
        try:
            data = json.loads(json_str)
            return self._calculate_depth(data)
        except json.JSONDecodeError:
            return 0
    
    def _calculate_depth(self, data, current=1):
        if isinstance(data, dict):
            if not data:
                return current
            return max(self._calculate_depth(v, current + 1) for v in data.values())
        elif isinstance(data, list):
            if not data:
                return current
            return max(self._calculate_depth(item, current + 1) for item in data)
        return current
    
    def get_keys(self, json_str):
        try:
            data = json.loads(json_str)
            if isinstance(data, dict):
                return self._get_all_keys(data)
            return []
        except json.JSONDecodeError:
            return []
    
    def _get_all_keys(self, data, prefix=""):
        keys = []
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            keys.append(full_key)
            if isinstance(value, dict):
                keys.extend(self._get_all_keys(value, full_key))
        return keys

def main():
    formatter = JSONFormatter()
    
    json_str = '{"name":"张三","age":25,"skills":["Python","Java"]}'
    
    print("美化输出:")
    print(formatter.beautify(json_str))
    
    print("\n压缩输出:")
    print(formatter.minify(json_str))
    
    print(f"\n验证结果: {formatter.validate(json_str)}")
    print(f"数据类型: {formatter.get_type(json_str)}")
    print(f"嵌套深度: {formatter.get_depth(json_str)}")


if __name__ == "__main__":
    main()
