# -----------------------------
# 题目：模板方法模式实现数据处理流程。
# -----------------------------

from abc import ABC, abstractmethod

class DataProcessor(ABC):
    def process(self, data):
        data = self.read_data(data)
        data = self.validate_data(data)
        data = self.transform_data(data)
        result = self.save_data(data)
        self.log_result(result)
        return result
    
    def read_data(self, data):
        print("读取数据...")
        return data
    
    @abstractmethod
    def validate_data(self, data):
        pass
    
    @abstractmethod
    def transform_data(self, data):
        pass
    
    def save_data(self, data):
        print(f"保存数据: {data}")
        return data
    
    def log_result(self, result):
        print(f"处理完成: {result}")

class CSVProcessor(DataProcessor):
    def validate_data(self, data):
        print("验证CSV格式...")
        if not isinstance(data, list):
            raise ValueError("CSV数据必须是列表")
        return data
    
    def transform_data(self, data):
        print("转换CSV数据...")
        return [item.strip() if isinstance(item, str) else item for item in data]

class JSONProcessor(DataProcessor):
    def validate_data(self, data):
        print("验证JSON格式...")
        if not isinstance(data, dict):
            raise ValueError("JSON数据必须是字典")
        return data
    
    def transform_data(self, data):
        print("转换JSON数据...")
        return {k: v.upper() if isinstance(v, str) else v for k, v in data.items()}

class XMLProcessor(DataProcessor):
    def validate_data(self, data):
        print("验证XML格式...")
        if not isinstance(data, str) or not data.startswith('<'):
            raise ValueError("XML数据必须是有效的XML字符串")
        return data
    
    def transform_data(self, data):
        print("转换XML数据...")
        return data.replace('<', '&lt;').replace('>', '&gt;')

def main():
    processors = {
        'csv': CSVProcessor(),
        'json': JSONProcessor(),
        'xml': XMLProcessor()
    }
    
    test_data = {
        'csv': ['  hello  ', 'world', '  test  '],
        'json': {'name': 'john', 'city': 'beijing'},
        'xml': '<root><item>test</item></root>'
    }
    
    for ptype, processor in processors.items():
        print(f"\n=== {ptype.upper()}处理器 ===")
        processor.process(test_data[ptype])


if __name__ == "__main__":
    main()
