# -----------------------------
# 题目：any和all函数。
# 描述：使用any和all检查列表元素条件。
# -----------------------------

def main():
    nums = [1, 2, 3, 4, 5]
    print(f"列表: {nums}")
    print(f"any > 3: {any(x > 3 for x in nums)}")
    print(f"all > 0: {all(x > 0 for x in nums)}")
    print(f"any == 0: {any(x == 0 for x in nums)}")


if __name__ == "__main__":
    main()
