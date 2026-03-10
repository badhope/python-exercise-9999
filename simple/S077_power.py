# -----------------------------
# 题目：计算幂。
# 描述：计算a的b次幂（不使用**）。
# -----------------------------

def power(a, b):
    result = 1
    for _ in range(b):
        result *= a
    return result

def main():
    print(f"2的10次方: {power(2, 10)}")


if __name__ == "__main__":
    main()
