# -----------------------------
# 题目：生成器基础。
# 描述：创建和使用生成器。
# -----------------------------

def count_up_to(max):
    count = 1
    while count <= max:
        yield count
        count += 1

def main():
    gen = count_up_to(5)
    for num in gen:
        print(num)


if __name__ == "__main__":
    main()
