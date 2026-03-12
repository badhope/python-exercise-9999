# -----------------------------
# 题目：实现文件重命名工具。
# 描述：批量重命名文件，支持多种命名规则。
# -----------------------------

import os
import re

class FileRenamer:
    def __init__(self, directory):
        self.directory = directory
    
    def add_prefix(self, prefix, pattern="*"):
        files = self._get_files(pattern)
        results = []
        for filename in files:
            new_name = prefix + filename
            results.append((filename, new_name))
        return results
    
    def add_suffix(self, suffix, pattern="*"):
        files = self._get_files(pattern)
        results = []
        for filename in files:
            name, ext = os.path.splitext(filename)
            new_name = name + suffix + ext
            results.append((filename, new_name))
        return results
    
    def replace_text(self, old_text, new_text, pattern="*"):
        files = self._get_files(pattern)
        results = []
        for filename in files:
            new_name = filename.replace(old_text, new_text)
            results.append((filename, new_name))
        return results
    
    def add_numbering(self, start=1, pattern="*"):
        files = self._get_files(pattern)
        results = []
        for i, filename in enumerate(files, start):
            name, ext = os.path.splitext(filename)
            new_name = f"{i:03d}_{name}{ext}"
            results.append((filename, new_name))
        return results
    
    def change_extension(self, new_ext, pattern="*"):
        files = self._get_files(pattern)
        results = []
        for filename in files:
            name, _ = os.path.splitext(filename)
            new_name = name + new_ext
            results.append((filename, new_name))
        return results
    
    def lowercase(self, pattern="*"):
        files = self._get_files(pattern)
        results = []
        for filename in files:
            new_name = filename.lower()
            results.append((filename, new_name))
        return results
    
    def _get_files(self, pattern):
        if not os.path.exists(self.directory):
            return []
        files = os.listdir(self.directory)
        if pattern == "*":
            return files
        regex = pattern.replace("*", ".*").replace("?", ".")
        return [f for f in files if re.match(regex, f)]
    
    def preview(self, operations):
        print("预览重命名结果:")
        for old_name, new_name in operations:
            print(f"  {old_name} -> {new_name}")
    
    def execute(self, operations):
        success = 0
        for old_name, new_name in operations:
            old_path = os.path.join(self.directory, old_name)
            new_path = os.path.join(self.directory, new_name)
            if os.path.exists(old_path) and old_name != new_name:
                os.rename(old_path, new_path)
                success += 1
        return success

def main():
    renamer = FileRenamer(".")
    
    operations = renamer.add_prefix("test_", "*.txt")
    renamer.preview(operations[:5])


if __name__ == "__main__":
    main()
