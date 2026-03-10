# -----------------------------
# 题目：格雷编码。
# 描述：生成n位格雷编码序列。
# -----------------------------

def gray_code(n):
    return [i ^ (i >> 1) for i in range(2**n)]

def main():
    print(f"2位格雷码: {gray_code(2)}")


if __name__ == "__main__":
    main()
