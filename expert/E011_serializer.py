# -----------------------------
# 题目：实现简单的序列化框架。
# 描述：支持自定义序列化器。
# -----------------------------

class Serializer:
    def serialize(self, obj):
        raise NotImplementedError
    
    def deserialize(self, data):
        raise NotImplementedError

class JSONSerializer(Serializer):
    import json
    
    def serialize(self, obj):
        return self.json.dumps(obj, ensure_ascii=False)
    
    def deserialize(self, data):
        return self.json.loads(data)

class XMLSerializer(Serializer):
    def serialize(self, obj):
        lines = ['<?xml version="1.0"?>']
        lines.append(self._to_xml(obj, 'root'))
        return '\n'.join(lines)
    
    def _to_xml(self, obj, tag):
        if isinstance(obj, dict):
            inner = ''.join(self._to_xml(v, k) for k, v in obj.items())
            return f'<{tag}>{inner}</{tag}>'
        elif isinstance(obj, list):
            inner = ''.join(self._to_xml(item, 'item') for item in obj)
            return f'<{tag}>{inner}</{tag}>'
        else:
            return f'<{tag}>{obj}</{tag}>'
    
    def deserialize(self, data):
        pass

class SerializationFactory:
    _serializers = {
        'json': JSONSerializer,
        'xml': XMLSerializer
    }
    
    @classmethod
    def get_serializer(cls, format_):
        if format_ in cls._serializers:
            return cls._serializers[format_]()
        raise ValueError(f"不支持的格式: {format_}")

def main():
    data = {"name": "张三", "age": 25, "skills": ["Python", "Java"]}
    
    json_ser = SerializationFactory.get_serializer('json')
    print(f"JSON: {json_ser.serialize(data)}")
    
    xml_ser = SerializationFactory.get_serializer('xml')
    print(f"XML:\n{xml_ser.serialize(data)}")


if __name__ == "__main__":
    main()
