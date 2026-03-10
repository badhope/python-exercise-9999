# -----------------------------
# 题目：快乐数。
# 描述：判断一个数是否为快乐数。
# -----------------------------

def is_happy(n):
    seen = set()
    while n != 1 and n not in seen:
        seen.add(n)
        n = sum(int(d)**2 for d in str(n))
    return n == 1

def main():
    print(f"19是快乐数: {is_happy(19)}")
    print(f"2是快乐数: {is_happy(2)}")


if __name__ == "__main__":
    main()
