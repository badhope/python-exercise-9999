# -----------------------------
# 题目：访问者模式实现文档元素处理。
# -----------------------------

class Visitor:
    def visit_text(self, element):
        pass
    
    def visit_image(self, element):
        pass
    
    def visit_table(self, element):
        pass

class DocumentElement:
    def accept(self, visitor):
        pass

class TextElement(DocumentElement):
    def __init__(self, text):
        self.text = text
    
    def accept(self, visitor):
        visitor.visit_text(self)

class ImageElement(DocumentElement):
    def __init__(self, src, alt):
        self.src = src
        self.alt = alt
    
    def accept(self, visitor):
        visitor.visit_image(self)

class TableElement(DocumentElement):
    def __init__(self, rows, cols, data):
        self.rows = rows
        self.cols = cols
        self.data = data
    
    def accept(self, visitor):
        visitor.visit_table(self)

class HTMLVisitor(Visitor):
    def visit_text(self, element):
        return f"<p>{element.text}</p>"
    
    def visit_image(self, element):
        return f'<img src="{element.src}" alt="{element.alt}">'
    
    def visit_table(self, element):
        html = "<table>"
        for row in element.data:
            html += "<tr>"
            for cell in row:
                html += f"<td>{cell}</td>"
            html += "</tr>"
        html += "</table>"
        return html

class MarkdownVisitor(Visitor):
    def visit_text(self, element):
        return element.text
    
    def visit_image(self, element):
        return f"![{element.alt}]({element.src})"
    
    def visit_table(self, element):
        md = "| " + " | ".join(element.data[0]) + " |\n"
        md += "| " + " | ".join(["---"] * len(element.data[0])) + " |\n"
        for row in element.data[1:]:
            md += "| " + " | ".join(row) + " |\n"
        return md

class Document:
    def __init__(self):
        self.elements = []
    
    def add_element(self, element):
        self.elements.append(element)
    
    def export(self, visitor):
        result = []
        for element in self.elements:
            result.append(element.accept(visitor))
        return "\n".join(result)

def main():
    doc = Document()
    doc.add_element(TextElement("这是一段文本"))
    doc.add_element(ImageElement("photo.jpg", "照片"))
    doc.add_element(TableElement(2, 2, [["姓名", "年龄"], ["张三", "25"]]))
    
    html_visitor = HTMLVisitor()
    md_visitor = MarkdownVisitor()
    
    print("=== HTML输出 ===")
    print(doc.export(html_visitor))
    print("\n=== Markdown输出 ===")
    print(doc.export(md_visitor))


if __name__ == "__main__":
    main()
