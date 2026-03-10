# -----------------------------
# 题目：sorted函数。
# 描述：使用sorted对列表和字典进行排序。
# -----------------------------

def main():
    nums = [3, 1, 4, 1, 5, 9]
    print(f"列表: {nums}")
    print(f"sorted: {sorted(nums)}")
    print(f"sorted reverse: {sorted(nums, reverse=True)}")
    
    text = "banana"
    print(f"字符串排序: {sorted(text)}")


if __name__ == "__main__":
    main()
