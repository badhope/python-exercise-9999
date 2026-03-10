# -----------------------------
# 题目：CSV文件操作。
# 描述：读取和写入CSV文件。
# -----------------------------

import csv

def main():
    with open("data.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Age"])
        writer.writerow(["Alice", 25])
        writer.writerow(["Bob", 30])
    
    with open("data.csv", "r") as f:
        reader = csv.reader(f)
        for row in reader:
            print(row)


if __name__ == "__main__":
    main()
