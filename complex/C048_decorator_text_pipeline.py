# -----------------------------
# 题目：装饰器模式实现文本处理管道。
# -----------------------------

class TextProcessor:
    def process(self, text):
        return text

class TextDecorator(TextProcessor):
    def __init__(self, processor):
        self.processor = processor
    
    def process(self, text):
        return self.processor.process(text)

class TrimDecorator(TextDecorator):
    def process(self, text):
        return super().process(text).strip()

class LowerCaseDecorator(TextDecorator):
    def process(self, text):
        return super().process(text).lower()

class UpperCaseDecorator(TextDecorator):
    def process(self, text):
        return super().process(text).upper()

class CapitalizeDecorator(TextDecorator):
    def process(self, text):
        return super().process(text).title()

class RemoveSpacesDecorator(TextDecorator):
    def process(self, text):
        return super().process(text).replace(' ', '')

class ReverseDecorator(TextDecorator):
    def process(self, text):
        return super().process(text)[::-1]

class MaskEmailDecorator(TextDecorator):
    def process(self, text):
        import re
        result = super().process(text)
        return re.sub(r'(\w{1,3})\w*@(\w+)', r'\1***@\2', result)

class MaskPhoneDecorator(TextDecorator):
    def process(self, text):
        import re
        result = super().process(text)
        return re.sub(r'(\d{3})\d{4}(\d{4})', r'\1****\2', result)

class HtmlEscapeDecorator(TextDecorator):
    def process(self, text):
        result = super().process(text)
        replacements = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        }
        for char, entity in replacements.items():
            result = result.replace(char, entity)
        return result

class TextPipeline:
    def __init__(self):
        self.processor = TextProcessor()
    
    def add(self, decorator_class):
        self.processor = decorator_class(self.processor)
        return self
    
    def process(self, text):
        return self.processor.process(text)

class TextProcessorFactory:
    @staticmethod
    def create_email_masker():
        return (TextPipeline()
                .add(TrimDecorator)
                .add(MaskEmailDecorator))
    
    @staticmethod
    def create_phone_masker():
        return (TextPipeline()
                .add(TrimDecorator)
                .add(MaskPhoneDecorator))
    
    @staticmethod
    def create_html_sanitizer():
        return (TextPipeline()
                .add(TrimDecorator)
                .add(HtmlEscapeDecorator))
    
    @staticmethod
    def create_normalizer():
        return (TextPipeline()
                .add(TrimDecorator)
                .add(LowerCaseDecorator)
                .add(RemoveSpacesDecorator))

def main():
    print("=== 邮箱脱敏 ===")
    email_processor = TextProcessorFactory.create_email_masker()
    print(email_processor.process("  zhangsan@example.com  "))
    
    print("\n=== 手机号脱敏 ===")
    phone_processor = TextProcessorFactory.create_phone_masker()
    print(phone_processor.process("13812345678"))
    
    print("\n=== HTML转义 ===")
    html_processor = TextProcessorFactory.create_html_sanitizer()
    print(html_processor.process("<script>alert('xss')</script>"))
    
    print("\n=== 文本标准化 ===")
    normalizer = TextProcessorFactory.create_normalizer()
    print(normalizer.process("  Hello World  "))
    
    print("\n=== 自定义管道 ===")
    custom_pipeline = (TextPipeline()
                       .add(TrimDecorator)
                       .add(CapitalizeDecorator)
                       .add(ReverseDecorator))
    print(custom_pipeline.process("  hello world  "))


if __name__ == "__main__":
    main()
