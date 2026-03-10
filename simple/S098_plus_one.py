# -----------------------------
# 题目：加一。
# 描述：将数组表示的数字加一。
# -----------------------------

def plus_one(digits):
    for i in range(len(digits) - 1, -1, -1):
        if digits[i] < 9:
            digits[i] += 1
            return digits
        digits[i] = 0
    return [1] + digits

def main():
    print(f"加一: {plus_one([1,2,3])}")


if __name__ == "__main__":
    main()
