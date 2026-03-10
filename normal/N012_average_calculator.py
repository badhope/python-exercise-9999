# -----------------------------
# 题目：求平均值。
# 描述：计算用户输入的一系列数字的平均值。
# -----------------------------

def calculate_average(numbers):
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)

def main():
    numbers = [10, 20, 30, 40, 50]
    print(f"数字: {numbers}")
    print(f"平均值: {calculate_average(numbers)}")


if __name__ == "__main__":
    main()
