# -----------------------------
# 题目：阿姆斯特朗数。
# 描述：判断一个数是否为水仙花数（阿姆斯特朗数）。
# -----------------------------

def is_armstrong(n):
    digits = [int(d) for d in str(n)]
    return sum(d**len(digits) for d in digits) == n

def main():
    for i in [153, 370, 371, 407, 100]:
        print(f"{i}: {'是' if is_armstrong(i) else '不是'}阿姆斯特朗数")


if __name__ == "__main__":
    main()
