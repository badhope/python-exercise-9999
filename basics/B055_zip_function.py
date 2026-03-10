# -----------------------------
# 题目：zip函数练习。
# 描述：使用zip函数合并两个列表为字典。
# -----------------------------

def main():
    keys = ['name', 'age', 'city']
    values = ['Alice', 25, 'Beijing']
    
    d = dict(zip(keys, values))
    print(f"合并为字典: {d}")
    
    for k, v in zip(keys, values):
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
