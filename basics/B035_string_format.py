# -----------------------------
# 题目：字符串格式化输出。
# 描述：使用 format()、f-string、% 三种方式格式化输出个人信息。
# -----------------------------

def main():
    name = "Alice"
    age = 25
    score = 95.5
    
    print("format(): My name is {}, age {}, score {:.1f}".format(name, age, score))
    print(f"f-string: My name is {name}, age {age}, score {score:.1f}")
    print("%%: My name is %s, age %d, score %.1f" % (name, age, score))


if __name__ == "__main__":
    main()
