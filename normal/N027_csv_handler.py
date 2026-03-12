# -----------------------------
# 题目：实现简单的CSV处理工具。
# 描述：读取、写入、转换CSV文件。
# -----------------------------

import csv
from io import StringIO

class CSVHandler:
    def __init__(self):
        self.data = []
        self.headers = []
    
    def read_from_string(self, csv_string, has_header=True):
        reader = csv.reader(StringIO(csv_string))
        rows = list(reader)
        if has_header and rows:
            self.headers = rows[0]
            self.data = rows[1:]
        else:
            self.data = rows
        return self.data
    
    def read_from_file(self, filepath, has_header=True, encoding='utf-8'):
        with open(filepath, 'r', encoding=encoding, newline='') as f:
            reader = csv.reader(f)
            rows = list(reader)
            if has_header and rows:
                self.headers = rows[0]
                self.data = rows[1:]
            else:
                self.data = rows
        return self.data
    
    def write_to_string(self, include_header=True):
        output = StringIO()
        writer = csv.writer(output)
        if include_header and self.headers:
            writer.writerow(self.headers)
        writer.writerows(self.data)
        return output.getvalue()
    
    def write_to_file(self, filepath, include_header=True, encoding='utf-8'):
        with open(filepath, 'w', encoding=encoding, newline='') as f:
            writer = csv.writer(f)
            if include_header and self.headers:
                writer.writerow(self.headers)
            writer.writerows(self.data)
    
    def get_column(self, column_name):
        if column_name not in self.headers:
            return []
        index = self.headers.index(column_name)
        return [row[index] for row in self.data if len(row) > index]
    
    def get_row(self, row_index):
        if 0 <= row_index < len(self.data):
            return self.data[row_index]
        return []
    
    def filter_rows(self, column_name, value):
        if column_name not in self.headers:
            return []
        index = self.headers.index(column_name)
        return [row for row in self.data if len(row) > index and row[index] == value]
    
    def sort_by_column(self, column_name, reverse=False):
        if column_name not in self.headers:
            return
        index = self.headers.index(column_name)
        self.data.sort(key=lambda x: x[index] if len(x) > index else '', reverse=reverse)
    
    def to_dict_list(self):
        if not self.headers:
            return []
        result = []
        for row in self.data:
            row_dict = {}
            for i, header in enumerate(self.headers):
                row_dict[header] = row[i] if i < len(row) else ''
            result.append(row_dict)
        return result
    
    def get_stats(self):
        return {
            "行数": len(self.data),
            "列数": len(self.headers),
            "列名": self.headers
        }

def main():
    csv_handler = CSVHandler()
    
    csv_string = """name,age,city
张三,25,北京
李四,30,上海
王五,28,广州"""
    
    csv_handler.read_from_string(csv_string)
    
    print("CSV统计:")
    stats = csv_handler.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n年龄列:")
    print(f"  {csv_handler.get_column('age')}")
    
    print("\n字典列表:")
    for item in csv_handler.to_dict_list():
        print(f"  {item}")


if __name__ == "__main__":
    main()
