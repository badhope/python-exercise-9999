# -----------------------------
# 题目：reversed函数。
# 描述：使用reversed反转序列。
# -----------------------------

def main():
    nums = [1, 2, 3, 4, 5]
    print(f"列表: {nums}")
    print(f"reversed: {list(reversed(nums))}")
    
    text = "hello"
    print(f"反转字符串: {''.join(reversed(text))}")


if __name__ == "__main__":
    main()
