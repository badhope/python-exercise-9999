# -----------------------------
# 题目：实现模板方法模式高级版。
# -----------------------------

from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class ProcessResult:
    success: bool
    data: Any = None
    error: str = None

class ProcessTemplate(ABC):
    def execute(self, *args, **kwargs) -> ProcessResult:
        try:
            self.validate(*args, **kwargs)
            data = self.preprocess(*args, **kwargs)
            result = self.process(data)
            output = self.postprocess(result)
            self.cleanup()
            return ProcessResult(success=True, data=output)
        except Exception as e:
            self.on_error(e)
            return ProcessResult(success=False, error=str(e))
    
    @abstractmethod
    def validate(self, *args, **kwargs):
        pass
    
    @abstractmethod
    def process(self, data: Any) -> Any:
        pass
    
    def preprocess(self, *args, **kwargs) -> Any:
        return kwargs if kwargs else args
    
    def postprocess(self, result: Any) -> Any:
        return result
    
    def cleanup(self):
        pass
    
    def on_error(self, error: Exception):
        print(f"处理错误: {error}")

class DataProcessor(ProcessTemplate):
    def validate(self, *args, **kwargs):
        if not args and not kwargs:
            raise ValueError("没有输入数据")
    
    def process(self, data: Any) -> Any:
        if isinstance(data, dict):
            return {k: str(v).upper() for k, v in data.items()}
        elif isinstance(data, (list, tuple)):
            return [str(item).upper() for item in data]
        return str(data).upper()

class FileProcessor(ProcessTemplate):
    def __init__(self, filename: str):
        self.filename = filename
        self.file = None
    
    def validate(self, *args, **kwargs):
        import os
        if not os.path.exists(self.filename):
            raise FileNotFoundError(f"文件不存在: {self.filename}")
    
    def preprocess(self, *args, **kwargs) -> List[str]:
        self.file = open(self.filename, 'r', encoding='utf-8')
        return self.file.readlines()
    
    def process(self, data: List[str]) -> List[str]:
        return [line.strip() for line in data if line.strip()]
    
    def cleanup(self):
        if self.file:
            self.file.close()

class TemplateBuilder:
    def __init__(self):
        self._validate_func = None
        self._preprocess_func = None
        self._process_func = None
        self._postprocess_func = None
        self._cleanup_func = None
        self._error_func = None
    
    def validate(self, func):
        self._validate_func = func
        return self
    
    def preprocess(self, func):
        self._preprocess_func = func
        return self
    
    def process(self, func):
        self._process_func = func
        return self
    
    def postprocess(self, func):
        self._postprocess_func = func
        return self
    
    def cleanup(self, func):
        self._cleanup_func = func
        return self
    
    def on_error(self, func):
        self._error_func = func
        return self
    
    def build(self) -> ProcessTemplate:
        builder = self
        
        class DynamicTemplate(ProcessTemplate):
            def validate(self, *args, **kwargs):
                if builder._validate_func:
                    builder._validate_func(*args, **kwargs)
            
            def preprocess(self, *args, **kwargs):
                if builder._preprocess_func:
                    return builder._preprocess_func(*args, **kwargs)
                return super().preprocess(*args, **kwargs)
            
            def process(self, data):
                if builder._process_func:
                    return builder._process_func(data)
                return data
            
            def postprocess(self, result):
                if builder._postprocess_func:
                    return builder._postprocess_func(result)
                return super().postprocess(result)
            
            def cleanup(self):
                if builder._cleanup_func:
                    builder._cleanup_func()
            
            def on_error(self, error):
                if builder._error_func:
                    builder._error_func(error)
                else:
                    super().on_error(error)
        
        return DynamicTemplate()

class TemplateRegistry:
    _templates: Dict[str, ProcessTemplate] = {}
    
    @classmethod
    def register(cls, name: str, template: ProcessTemplate):
        cls._templates[name] = template
    
    @classmethod
    def get(cls, name: str) -> Optional[ProcessTemplate]:
        return cls._templates.get(name)
    
    @classmethod
    def execute(cls, name: str, *args, **kwargs) -> ProcessResult:
        template = cls.get(name)
        if template:
            return template.execute(*args, **kwargs)
        return ProcessResult(success=False, error=f"模板 {name} 未注册")

def main():
    print("=== 数据处理器 ===")
    processor = DataProcessor()
    result = processor.execute(name="张三", age=25)
    print(f"结果: {result}")
    
    print("\n=== 模板构建器 ===")
    template = (TemplateBuilder()
                .validate(lambda *a, **kw: None if a or kw else ValueError("无数据"))
                .process(lambda data: [x * 2 for x in data] if isinstance(data, list) else data)
                .postprocess(lambda r: {"result": r})
                .build())
    
    result = template.execute([1, 2, 3, 4, 5])
    print(f"结果: {result}")
    
    print("\n=== 模板注册表 ===")
    TemplateRegistry.register("uppercase", DataProcessor())
    
    result = TemplateRegistry.execute("uppercase", text="hello world")
    print(f"结果: {result}")
    
    print("\n=== 错误处理 ===")
    def validate_positive(*args, **kwargs):
        value = kwargs.get('value', 0)
        if value <= 0:
            raise ValueError("值必须为正数")
    
    template = (TemplateBuilder()
                .validate(validate_positive)
                .process(lambda data: data.get('value') ** 2)
                .on_error(lambda e: print(f"自定义错误处理: {e}"))
                .build())
    
    result = template.execute(value=-5)
    print(f"结果: {result}")


if __name__ == "__main__":
    main()
