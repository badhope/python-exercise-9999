# -----------------------------
# 题目：filter函数练习。
# 描述：使用filter函数过滤列表中的元素。
# -----------------------------

def main():
    numbers = list(range(1, 11))
    evens = list(filter(lambda x: x % 2 == 0, numbers))
    print(f"1-10: {numbers}")
    print(f"偶数: {evens}")
    
    words = ['hello', 'world', 'python', 'hi']
    long_words = list(filter(lambda w: len(w) > 4, words))
    print(f"长单词: {long_words}")


if __name__ == "__main__":
    main()
