# -----------------------------
# 题目：JSON文件操作。
# 描述：读取和写入JSON文件。
# -----------------------------

import json

def main():
    data = {"name": "Alice", "age": 25, "city": "Beijing"}
    
    with open("data.json", "w") as f:
        json.dump(data, f)
    
    with open("data.json", "r") as f:
        loaded = json.load(f)
    print(f"加载数据: {loaded}")


if __name__ == "__main__":
    main()
